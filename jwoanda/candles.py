from __future__ import print_function

try:
    import cPickle as pickle
except:
    import pickle
try:
    import lzma
except ImportError:
    from backports import lzma
import itertools
import os
import sys
import logging
import pathlib

import numpy as np
import pandas as pd
import v20
from xdg import BaseDirectory

from jwoanda.instenum import Instruments
from jwoanda.enums import Granularity, VolumeGranularity
from jwoanda.utils import get_items

class MultiCandles(object):
    """MultiCandles class: candles for many instruments"""

    def __init__(self, instruments=None, granularity=None, size=1000, clist=None):
        """MultiCandles constructor

        Args:
            instruments: list of Instruments enums
            granularity: Granularity
            size: starting size of Candles
            clist: initialize the object using a dictionary {Instruments: Candles}
        """
        self._data = {}
        if instruments is not None:
            if isinstance(instruments[0], Instruments):
                self._instruments = instruments
            else:
                raise Exception("Not a valid instrument: type={}.".format(type(instruments[0])))
            for instrument in self._instruments:
                self._data[instrument] = Candles(instrument=instrument, granularity=granularity, size=size)
        if clist is not None:
            self._instruments = []
            for c in clist:
                self._instruments.append(c.instrument)
                self._data[c.instrument] = c
                #print(type(c))


    @property
    def instruments(self):
        return self._instruments


    @property
    def granularity(self):
        return self.candles(self.instruments[0]).granularity


    @property
    def year(self):
        return self.candles(self.instruments[0]).year


    @property
    def ncandles(self):
        #print(type(self.candles(self.instruments[0])))
        return self.candles(self.instruments[0]).ncandles


    def candles(self, instrument):
        return self._data[instrument]


    def setcandles(self, instrument, data):
        self._data[instrument] = data


    def head(self, size, inplace=False):
        ncandles = self._data[self._instruments[0]].ncandles
        if size > ncandles:
            size = ncandles

        tmp = {}
        for instrument in self._instruments:
            tmp[instrument] = self._data[instrument].head(size)

        if inplace:
            self._data = tmp
        else:
            return tmp

    def resize(self, size):
        for instrument in self._instruments:
            self._data[instrument].resize(size)


    def tail(self, size, inplace=False, oneincomplete=0):
        ncandles = self._data[self._instruments[0]].ncandles
        if size > ncandles:
            size = ncandles

        tmp = {}
        for instrument in self._instruments:
            tmp[instrument] = self._data[instrument].tail(size, oneincomplete=oneincomplete)

        if inplace:
            self._data = tmp
        else:
            return tmp


    def align(self):
        dflist = []
        for instrument, c in get_items(self._data):
            dflist.append(c.DataFrame())

        for cnt in range(0, len(dflist)):
            print("cnt = ", cnt, " len = ", len(dflist[cnt]))

        for cnt1, cnt2 in itertools.permutations(range(0, len(dflist)), 2):
            df1, df2 = dflist[cnt1].align(dflist[cnt2])
            dflist[cnt1] = df1
            dflist[cnt2] = df2

        for cnt in range(0, len(dflist)):
            print("cnt = ", cnt, " len = ", len(dflist[cnt]))

        for cnt, key in enumerate(self._data):
            self._data[key] = Candles(instrument=self.instruments[cnt], granularity=self.granularity, df=dflist[cnt])



class Candles(object):
    def __init__(self, instrument, granularity, year="", size=1000, df=None, nparr=None, cdict=None):

        self._instrument = None
        self._granularity = None

        self.instrument = instrument
        self.granularity = granularity
        self._year = str(year)

        if df is not None:
            size = len(df)
            self._data = self.zerodata(size)
            for c in self._data.dtype.names:
                if c == 'time':
                    continue
                self._data[c] = df[c].values
            self._data['time'] = df.index
            self._ncandles = size
            return

        if nparr is not None:
            self._data = nparr
            self._ncandles = len(nparr)
            return

        if cdict is not None:
            ncandles = len(cdict.get('volume'))
            self._data = self.zerodata(ncandles)
            for key, val in get_items(cdict):
                self._data[key] = val
            self._ncandles = ncandles
            return

        self._data = self.zerodata(size)
        self._ncandles = 0


    def zerodata(self, size):
        return np.zeros(size, dtype=[('openBid', np.float64), ('openAsk', np.float64),
                                     ('highBid', np.float64), ('highAsk', np.float64),
                                     ('lowBid', np.float64), ('lowAsk', np.float64),
                                     ('closeBid', np.float64), ('closeAsk', np.float64),
                                     ('volume', np.float64), ('time', np.float64),
                                     ('complete', np.uint8)])


    def resize(self, newsize):
        self._data = np.append(self._data, self.zerodata(newsize - len(self._data)))


    @property
    def data(self):
        return self._data


    @property
    def ncandles(self):
        return self._ncandles


    @ncandles.setter
    def ncandles(self, value):
        if value > self._data.size:
            self.resize(self._data.size * 2)
        self._ncandles = value


    @property
    def instrument(self):
        return self._instrument


    @instrument.setter
    def instrument(self, instrument):
        if isinstance(instrument, Instruments):
            self._instrument = instrument
        else:
            raise Exception("Not a valid instrument: type={}".format(type(instrument)))


    @property
    def granularity(self):
        return self._granularity


    @granularity.setter
    def granularity(self, granularity):
        if isinstance(granularity, Granularity) or isinstance(granularity, VolumeGranularity):
            self._granularity = granularity
        else:
            raise Exception("Not a valid granularity: type={}".format(type(granularity)))

    @property
    def year(self):
        return self._year


    @year.setter
    def year(self, year):
        self._year = str(year)


    def set(self, index, candle):
        if index >= len(self._data):
            self.resize(len(self._data) * 2)

        if isinstance(candle, v20.instrument.Candlestick):
            self._data[index] = (candle.bid.o,
                                 candle.ask.o,
                                 candle.bid.h,
                                 candle.ask.h,
                                 candle.bid.l,
                                 candle.ask.l,
                                 candle.bid.c,
                                 candle.ask.c,
                                 candle.volume,
                                 candle.time,
                                 candle.complete)
        else:
            self._data[index] = (candle['openBid'],
                                 candle['openAsk'],
                                 candle['highBid'],
                                 candle['highAsk'],
                                 candle['lowBid'],
                                 candle['lowAsk'],
                                 candle['closeBid'],
                                 candle['closeAsk'],
                                 candle['volume'],
                                 candle['time'],
                                 candle['complete'])


    def add(self, candle):
        self.set(self._ncandles, candle)
        self._ncandles += 1


    def head(self, newsize, inplace=False):
        if newsize > self._data.size:
            newsize = self._data.size

        reqcandles = self._data[:newsize]
        if inplace:
            self._data = np.array(reqcandles)
            self.ncandles = newsize
        else:
            return Candles(instrument=self.instrument, granularity=self.granularity, year=self.year, nparr=reqcandles)


    def tail(self, size, inplace=False, oneincomplete=0):
        if size > self.ncandles:
            size = self.ncandles

        reqcandles = self._data[self.ncandles + oneincomplete - size:self.ncandles + oneincomplete]

        if inplace:
            self._data = np.array(reqcandles)
        else:
            return Candles(instrument=self.instrument, granularity=self.granularity, year=self.year, nparr=reqcandles)


    def fill(self, oandacandles):
        for candle in oandacandles:
            self.add(candle)


    def getfilename(self, datadir=None):
        if datadir is None:
            datadir = BaseDirectory.save_data_path("jwoanda")

        pythonver = "py%d%d" % (sys.version_info.major, sys.version_info.minor)
        directory = os.path.join(datadir, "history", self.instrument.name)
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

        filename = "%s/%s-%s-%s-%s.history" % (directory, self.instrument.name, self.granularity.name, self.year, pythonver)
        return filename


    def load(self, datadir=None):
        filename = self.getfilename(datadir)

        logging.info("Reading %s @ %s from %s", self.instrument.name, self.granularity.name, filename)

        if not os.path.isfile(filename):
            logging.error("File not found")
            raise Exception("File not found")

        with lzma.open(filename, mode='rb') as f:
            data = pickle.load(f)
            self._data = data['candles']
            self._ncandles = data['ncandles']
            self._instrument = data['instrument']
            self._granularity = data['granularity']
            self._year = data['year']


    def save(self, datadir=None):
        filename = self.getfilename(datadir)

        data = {}
        data['candles'] = self._data
        data['ncandles'] = self._ncandles
        data['instrument'] = self._instrument
        data['granularity'] = self._granularity
        data['year'] = self.year
        f = lzma.open(filename, mode='wb')
        pickle.dump(data, f)
        f.close()


    def DataFrame(self):
        return pd.DataFrame({'openAsk':  self._data['openAsk'],
                             'highAsk':  self._data['highAsk'],
                             'lowAsk':   self._data['lowAsk'],
                             'closeAsk': self._data['closeAsk'],
                             'openBid':  self._data['openBid'],
                             'highBid':  self._data['highBid'],
                             'lowBid':   self._data['lowBid'],
                             'closeBid': self._data['closeBid'],
                             'complete': self._data['complete'],
                             'volume':   self._data['volume']},
                            index=self._data['time'])


    def append(self, candles):
        self._data = np.append(self._data, candles._data)
        self.ncandles += candles.ncandles


    def reduce(self, start, end):
        self._data = self._data[np.logical_and(self._data['time'] >= start, self._data['time'] <= end)]
        self.ncandles = len(self._data)
