from datetime import datetime
import logging
import time
from abc import ABCMeta, abstractmethod
from six import with_metaclass

from progressbar import Bar, ETA, Percentage, ProgressBar
import v20

from jwoanda.candleresize import resizebyvolume_cython
from jwoanda.candles import Candles
from jwoanda.enums import Granularity, VolumeGranularity
from jwoanda.instenum import Instruments
from jwoanda.oandaaccount import oandaenv


def floattostr(x, n):
    return "{:.{}f}".format(x, n)


class BaseHistoryManager(object, with_metaclass(ABCMeta)):
    def __init__(self):
        self._indicies = {}
        self._candles = {}

    @abstractmethod
    def getcandles(self, i, g, count):
        pass

    @abstractmethod
    def currtime(self):
        pass


class RealHistoryManager(BaseHistoryManager):
    def __init__(self, iglist=None):
        super(RealHistoryManager, self).__init__()
        self._ready = {}
        if iglist is not None:
            for i, g in iglist:
                self._candles[(i, g)] = Candles(i, g)
                self._indicies[(i, g)] = 0


    def add(self, i, g):
        if self._candles.get((i, g)) is None:
            self._candles[(i, g)] = Candles(i, g)
            self._indicies[(i, g)] = 0


    def getcandles(self, i, g, count):
        idx = self._indicies[(i,g)]
        if count>=idx:
            return None
        return self._candles[(i, g)]._data[idx-count:idx]


    def addCandle(self, i, g, candle):
        self._candles[(i, g)].add(candle)
        self._indicies[(i, g)] += 1


    def currtime(self):
        return float(datetime.now().strftime('%s.%f'))



class BTHistoryManager(BaseHistoryManager):

    def __init__(self, instruments, granularity, start, end):
        super(BTHistoryManager, self).__init__()
        self._granularity = granularity
        self._instruments = instruments
        self._first = instruments[0]

        for i in instruments:
            self._candles[i] = getcandles(i, granularity, start, end)
            self._indicies[i] = 0


    def getcandles(self, i, g, count):
        idx = self._indicies[i]
        if count>=idx:
            return None
        return self._candles[i]._data[idx-count:idx]


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
