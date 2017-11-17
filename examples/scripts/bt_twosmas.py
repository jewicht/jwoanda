#!/usr/bin/python

from __future__ import print_function

import logging
import sys
#import multiprocessing
#from functools import partial

import numpy as np
from sklearn.model_selection import GridSearchCV
from scipy import optimize

import talib as ta

from jwoanda.history import HistoryManager

from jwoanda.strategies.twosmas import TwoSMAsStrategy

from jwoanda.backtests.simplebacktest import SimpleBacktest
from jwoanda.backtests.candlesbacktest import CandlesBacktest
from jwoanda.backtests.fullcandlesbacktest import FullCandlesBacktest
from jwoanda.backtests.ticksbacktest import TicksBacktest
from jwoanda.backtests.mcandlesbacktest import MCandlesBacktest

from jwoanda.enums import VolumeGranularity, Granularity
from jwoanda.instenum import Instruments
from jwoanda.oandaaccount import oandaenv




def backtest2smas(candles):
    strat = TwoSMAsStrategy(candles.instrument, candles.granularity, units=1, shortperiod=30, longperiod=60, matype=ta.MA_Type.KAMA)#, stoploss=20)#, trailingstop=10)
    #bt = SimpleBacktest(candles, strat, saveportfolio=True, plot=True)
    #bt.start()
    bt = CandlesBacktest(candles, strat, saveportfolio=True, progressbar=True)
    #bt = FullCandlesBacktest(strat, saveportfolio=True, progressbar=True, candlesperc=0.05)
    return bt.start()



def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s')

    if len(sys.argv) < 3:
        print(sys.argv[0] + " granularity instrument1 instrument2 instrument3 ...")
        return

    granularity = sys.argv[1]
    if 'VOL' in granularity:
        granularity = VolumeGranularity(int(granularity.replace('VOL', '')))
    else:
        granularity = Granularity[granularity]
        
    instruments = []
    for i in range(2, len(sys.argv)):
        instrument = Instruments[sys.argv[i]]
        year = "2016"
        candles = HistoryManager.getcandles(instrument, granularity, year)
        profit = backtest2smas(candles)
        print(instrument.name, profit)
        #    granularity = "VOL100"
        #    granularity = "S5"
        #    granularity = Granularity.M15


if __name__ == "__main__":
    main()
