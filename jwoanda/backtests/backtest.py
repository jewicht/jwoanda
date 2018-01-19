import os
import sys
try:
    import lzma
except ImportError:
    from backports import lzma
import logging
try:
    import cPickle as pickle
except:
    import pickle
from abc import ABCMeta, abstractmethod
from six import with_metaclass
import numpy as np
import pathlib

from jwoanda.strategy import BaseStrategy
from jwoanda.portfolio.btportfolio import BTPortfolio
from jwoanda.oandaaccount import oandaenv

class Backtest(object, with_metaclass(ABCMeta)):

    def __init__(self, strategy, start, end, **kwargs):
        if not isinstance(strategy, BaseStrategy):
            raise Exception("Not a valid strategy")

        self._strategy = strategy

        self._startdate = start
        self._enddate = end
        
        _portfolio = kwargs.get('portfolio')
        if _portfolio is None:
            self._strategy.portfolio = BTPortfolio()
        else:
            self._strategy.portfolio = _portfolio

        self._showprogressbar = kwargs.get("progressbar", True)
        self._saveportfolio = kwargs.get("saveportfolio", False)
        self._includedate = kwargs.get("includedate", False)
        self._saveindatadir = kwargs.get("saveindatadir", False)

    @property
    def granularity(self):
        return self.strategy.granularity

    @property
    def showprogressbar(self):
        return self._showprogressbar

    @property
    def saveportfolio(self):
        return self._saveportfolio

    @property
    def strategy(self):
        return self._strategy


    @property
    def portfolio(self):
        return self.strategy.portfolio


    @property
    def instrument(self):
        return self.strategy.instrument


    @property
    def instruments(self):
        return self.strategy.instruments


    @abstractmethod
    def start(self):
        pass


    def randomtickgenerator(self, candle, instrument, cmt=None):
        openAsk = candle["openAsk"]
        openBid = candle["openBid"]
        highAsk = candle["highAsk"]
        highBid = candle["highBid"]
        lowAsk = candle["lowAsk"]
        lowBid = candle["lowBid"]
        closeAsk = candle["closeAsk"]
        closeBid = candle["closeBid"]
        volume = np.uint32(candle["volume"])
        time = candle["time"]

        spread = 0.5 * ((highAsk - highBid) + (lowAsk - lowBid))
        if volume == 0:
            return

        if volume == 1:
            t = (instrument, time, openBid, openAsk)
            self.tickoperation(t, cmt)
            return

        #        ticks = np.cumsum(np.random.uniform(-0.5, 0.5, volume))
        #        tmin = np.min(ticks)
        #        tmax = np.max(ticks)
        #        ticks = lowBid + (highBid - lowBid) * (ticks - tmin) / (tmax - tmin)
        ticks = np.empty(volume)
        ticks[0] = openBid
        ticks[1:(volume-1)] = np.random.uniform(lowBid, highBid, volume - 2)
        ticks[volume-1] = closeBid

        for tick in ticks:
            t = (instrument, time, tick, tick + spread)
            self.tickoperation(t, cmt)


    def tickoperation(self, tick, cmt=None):
        instrument, time, bid, ask = tick
        self.portfolio.setprice(instrument, (time, bid, ask))
        self.portfolio.checkTPSL(tick)
        if cmt is not None:
            cmt.addTick(tick)


    def lineartickgenerator(self, candle, instrument, cmt=None):
        openAsk = candle["openAsk"]
        openBid = candle["openBid"]
        highAsk = candle["highAsk"]
        highBid = candle["highBid"]
        lowAsk = candle["lowAsk"]
        lowBid = candle["lowBid"]
        closeAsk = candle["closeAsk"]
        closeBid = candle["closeBid"]
        volume = candle["volume"]
        time = candle["time"]
        spread = 0.5 * ((highAsk - highBid) + (lowAsk - lowBid))

        if volume == 0:
            return

        if volume == 1:
            t = (instrument, time, openBid, openAsk)
            self.tickoperation(t, cmt)
            return

        if np.random.random_sample() > 0.5:
            highAsk, highBid, lowAsk, lowBid = lowAsk, lowBid, highAsk, highBid


        len1 = 1.
        
        #go from open to high

        #go from high to low

        #go from low to close


    def simpletickgenerator(self, candle, instrument, cmt=None):

        openAsk = candle["openAsk"]
        openBid = candle["openBid"]
        highAsk = candle["highAsk"]
        highBid = candle["highBid"]
        lowAsk = candle["lowAsk"]
        lowBid = candle["lowBid"]
        closeAsk = candle["closeAsk"]
        closeBid = candle["closeBid"]
        volume = candle["volume"]
        time = candle["time"]

        t1 = (instrument, time, openBid, openAsk)
        t2 = (instrument, time, highBid, highAsk)
        t3 = (instrument, time, lowBid, lowAsk)
        t4 = (instrument, time, closeBid, closeAsk)

        self.tickoperation(t1, cmt)
        if np.random.random_sample() > 0.5:
            self.tickoperation(t2, cmt)
            self.tickoperation(t3, cmt)
        else:
            self.tickoperation(t3, cmt)
            self.tickoperation(t2, cmt)
        self.tickoperation(t4, cmt)


    def save(self, filename=None):
        cdict = {}
        cdict['portfolio'] = self.portfolio
        cdict['options'] = self.strategy.options

        directory = 'backtests'
        if self._saveindatadir:
            directory = os.path.join(oandaenv.datadir, directory)

        pathlib.Path(directory).mkdir(parents=True, exist_ok=True) 

        if filename is None:
            instlist = '-'.join([instr.name for instr in self.strategy.instruments])
            filename = '-'.join([type(self).__name__, self.strategy.name, instlist, self.granularity.name, self._startdate, self._enddate])
            if self._includedate:
                mydate = self.portfolio._startdate.strftime("%Y%m%d%H%M")
                filename += mydate

            filename += '.backtest'
                                
        filename = os.path.join(directory, filename)
        logging.info("Saving backtest data to %s", filename)
        
        f = lzma.open(filename, mode='wb')
        pickle.dump(cdict, f)
        f.close()
