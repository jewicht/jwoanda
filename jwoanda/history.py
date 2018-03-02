from datetime import datetime
import logging
import time
from abc import ABCMeta, abstractmethod
from six import with_metaclass

from progressbar import Bar, ETA, Percentage, ProgressBar
import v20

from jwoanda.resizebyvolume import resizebyvolume_cython
from jwoanda.candles import Candles
from jwoanda.multicandles import MultiCandles
from jwoanda.enums import Granularity, VolumeGranularity
from jwoanda.instenum import Instruments
from jwoanda.oandaaccount import oandaenv


def floattostr(x, n):
    return "{:.{}f}".format(x, n)


class BaseHistoryManager(object, with_metaclass(ABCMeta)):
    def __init__(self):
        self._indicies = {}
        self._candles = {}


    def getcandles(self, i, g, count):
        idx = self._indicies[(i,g)]
        if count>=idx:
            return None
        return self._candles[(i, g)]._data[idx-count:idx]


    @abstractmethod
    def currtime(self):
        pass


class RealHistoryManager(BaseHistoryManager):
    def __init__(self, iglist):
        super(RealHistoryManager, self).__init__()
        self._ready = {}
        for i, g in iglist:
            self._candles[(i,g)] = Candles(i, g)
            self._indicies[(i,g)] = 0
            self._ready[(i,g)] = False


    def isready(self, i, g):
        return self._ready[(i,g)]


    def setready(self, i, g, b):
        self._ready[(i,g)] = b


    def addCandle(self, i, g, candle):
        self._candles[(i,g)].add(candle)
        self._indicies[(i,g)] += 1


    def currtime(self):
        return float(datetime.now().strftime('%s.%f'))



class BTHistoryManager(BaseHistoryManager):

    def __init__(self, iglist, start, end):
        super(BTHistoryManager, self).__init__()
        self._first = iglist[0]

        for i, g in iglist:
            self._candles[(i,g)] = getcandles(i, g, start, end)
            self._indicies[(i,g)] = 0

    def currtime(self):
        return self._candles[self._first].data[self._indicies[self._first]]['time']

    def mintime(self):
        c = self._candles[self._first]
        return c.data[0]['time']

    def maxtime(self):
        c = self._candles[self._first]
        return c.data[-1]['time']

    def iteratetime(self):
        c = self._candles[self._first]
        idx = self._indicies[self._first]
        if (idx < len(c) - 1):
            idx += 1
            self._indicies[self._first] = idx
            return True
        else:
            return False

    

def getmulticandles(instruments, gran, start, end):
    clist = []
    for instrument in instruments:
        candles = getcandles(instrument, gran, start, end)
        clist.append(candles)
    mcandles = MultiCandles(clist=clist)
    mcandles.align()
    return mcandles


def getcandles(instrument, gran, start, end):
    if not isinstance(instrument, Instruments):
        raise Exception("Instrument {} not understood".format(instrument))
    if not isinstance(gran, Granularity) and not isinstance(gran, VolumeGranularity):
        raise Exception("Granularity {} not understood".format(gran))

    dts = datetime.strptime(start, "%Y%m%d")
    dte = datetime.strptime(end, "%Y%m%d")

    candles = None
    for year in range(dts.year, dte.year + 1):
        if isinstance(gran, VolumeGranularity):
            _s5candles = _getcandles(instrument, Granularity.S5, year)
            _candles = resizebyvolume(_s5candles, gran.volume)
        else:
            _candles = _getcandles(instrument, gran, year)
        if len(_candles.data) != _candles.ncandles:
            logging.error('len(_candles.data) != _candles.ncandles')
        if candles is None:
            candles = _candles
        else:
            candles.append(_candles)

    #reduce to requested range
    # TODO
    fdts = float(dts.strftime("%s"))
    fdte = float(dte.strftime("%s"))
    candles.reduce(fdts, fdte)
    return candles



def _getcandles(instrument, gran, year):
    try:
        candles = Candles(instrument=instrument, granularity=gran)
        candles.load(year, datadir=oandaenv.datadir)
        return candles
    except:
        return _downloadyearlydata(instrument, gran, year)


def resizebyvolume(candles, maxvolume):
    logging.info("Resizing %s %s to %d", candles.instrument.name, candles.granularity.name, maxvolume)
    cdict = resizebyvolume_cython(candles, maxvolume)
    newcandles = Candles(candles.instrument,
                         granularity=VolumeGranularity(maxvolume),
                         cdict=cdict)
    return newcandles


def _resizebyvolume_python(candles, maxvolume):
    logging.info("Resizing %s %s to %d", candles.instrument.name, candles.granularity.name, maxvolume)

    totvolume = candles.data["volume"].sum()
    maxentries = int(1.2 * totvolume / maxvolume)

    logging.debug("totvolume = %d", totvolume)
    newcandles = Candles(size=maxentries, instrument=candles.instrument, granularity=VolumeGranularity(maxvolume))
    
    volume = 0
    
    for candle in candles.data:
        
        if not candle["complete"]:
            continue

        if volume == 0:
            openAsk = candle["openAsk"]
            openBid = candle["openBid"]
            highAsk = candle["highAsk"]
            highBid = candle["highBid"]
            lowAsk = candle["lowAsk"]
            lowBid = candle["lowBid"]
            closeAsk = candle["closeAsk"]
            closeBid = candle["closeBid"]
            opentime = candle["time"]#append(index)#   = index
            
        volume += candle["volume"]

        if candle["highAsk"] > highAsk:
            highAsk = candle["highAsk"]
        if candle["highBid"] > highBid:
            highBid = candle["highBid"]
        if candle["lowAsk"] < lowAsk:
            lowAsk = candle["lowAsk"]
        if candle["lowBid"] < lowBid:
            lowBid = candle["lowBid"]

        if volume >= maxvolume:
            closeAsk = candle["closeAsk"]
            closeBid = candle["closeBid"]
            closetime = candle["time"]#append(index)

            volcandle = {
                'openBid': openBid, 'openAsk': openAsk,
                'highBid': highBid, 'highAsk': highAsk,
                'lowBid': lowBid, 'lowAsk': lowAsk,
                'closeBid': closeBid, 'closeAsk': closeAsk,
                'volume' : volume, 'time': opentime, 'complete': True
            }
            newcandles.add(volcandle)

            volume = 0

        #add a last non complete candle
    if volume > 0:
        volcandle = {
            'openBid': openBid, 'openAsk': openAsk,
            'highBid': highBid, 'highAsk': highAsk,
            'lowBid': lowBid, 'lowAsk': lowAsk,
            'closeBid': closeBid, 'closeAsk': closeAsk,
            'volume' : volume, 'time': opentime, 'complete': False
        }
        newcandles.add(volcandle)

    logging.debug("resize fcn lowAsk = %f volume = %f complete = %d", lowAsk, volume, False)
    
    newcandles.head(newcandles.ncandles, inplace=True)
    lastcandle = candles.data[candles.ncandles - 1]
    logging.debug("resize fcn lowAsk = %f volume = %f complete = %d", lastcandle["lowAsk"], lastcandle["volume"], lastcandle["complete"])
    
    lastcandle = newcandles.data[newcandles.ncandles - 1]
    logging.debug("resize fcn lowAsk = %f volume = %f complete = %d", lastcandle["lowAsk"], lastcandle["volume"], lastcandle["complete"])
    
    return newcandles


def _downloadyearlydata(instrument, gran, year, showpbar=True):
    year = int(year)
    start_date = float(datetime(year, 1, 1, 0, 0).strftime('%s'))
    end_date = float(datetime(year, 12, 31, 23, 59).strftime('%s'))
    now = float(datetime.now().strftime('%s')) + 24 * 3600
    if now < end_date:
        end_date = now
    candles = downloadhistoricaldata(instrument, gran, start_date, end_date, showpbar)
    if candles is None:
        raise Exception("Couldn't download data")
    candles.save(year, datadir=oandaenv.datadir)
    return candles


def downloadcandles(instrument, granularity, count, fromTime=None):
    api = oandaenv.api()
    ntries = 0
    while ntries < 3:
        try:
            if fromTime is None:
                response = api.instrument.candles(instrument=instrument,
                                                  granularity=granularity,
                                                  count=count,
                                                  price='BA')
            else:
                response = api.instrument.candles(instrument=instrument,
                                                  granularity=granularity,
                                                  fromTime=fromTime,
                                                  count=count,
                                                  price='BA')
            if response.status == 200:
                return response.get('candles')
            else:
                ntries += 1
        except v20.errors.V20ConnectionError:
            logging.error('V20ConnectionError for %s', instrument)
            time.sleep(1)
            ntries += 1
        except v20.errors.V20Timeout:
            logging.error('V20Timeout for %s', instrument)
            time.sleep(1)
            ntries += 1
            continue
    return None


def downloadhistoricaldata(instrument, gran, start_date, end_date, showpbar=True):

    if not isinstance(instrument, Instruments):
        raise Exception("Not a proper instrument")
    
    if not isinstance(gran, Granularity):
        raise Exception("Not a proper granularity")

    begin_date = start_date
    count = 5000
    logging.info("Downloading history for %s %s from %s to %s", instrument.name, gran.name, datetime.fromtimestamp(start_date), datetime.fromtimestamp(end_date))

    candles = Candles(size=int(1.1*(end_date-start_date)/gran.value),
                      instrument=instrument,
                      granularity=gran)

    if showpbar:
        pbar = ProgressBar(widgets=['Downloading: ',
                                    Percentage(),
                                    Bar(),
                                    ETA()],
                           max_value=int(end_date-start_date)).start()

    while start_date < end_date:

        rescandles = downloadcandles(instrument.name, gran.name, count=count, fromTime=start_date)

        if rescandles is not None:
            for candle in rescandles:
                if float(candle.time) < end_date:
                    candles.add(candle)

            firstcandle = rescandles[0]
            lastcandle = rescandles[-1]
            logging.debug("first candle = %s", datetime.fromtimestamp(float(firstcandle.time)))
            logging.debug("last candle  = %s", datetime.fromtimestamp(float(lastcandle.time)))
            start_date = gran.value + float(lastcandle.time)

            if len(rescandles) != count:
                logging.warning("We received only %d candles, exiting", len(rescandles))
                break

            if showpbar:
                pbar.update(int(start_date - begin_date) % pbar.max_value)
        else:
            logging.error("We received nothing from Oanda.")
            return

    candles.head(candles.ncandles, inplace=True)

    if showpbar:
        pbar.finish()
    return candles
