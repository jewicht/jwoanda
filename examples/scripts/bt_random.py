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

from jwoanda.strategies.random import RandomStrategy

from jwoanda.backtests.simplebacktest import SimpleBacktest
from jwoanda.backtests.candlesbacktest import CandlesBacktest
from jwoanda.backtests.fullcandlesbacktest import FullCandlesBacktest
from jwoanda.backtests.ticksbacktest import TicksBacktest
from jwoanda.backtests.mcandlesbacktest import MCandlesBacktest

from jwoanda.enums import VolumeGranularity, Granularity
from jwoanda.instenum import Instruments
from jwoanda.oandaaccount import oandaenv


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
        
        strat = RandomStrategy(instrument, granularity, units=1)
        #bt = SimpleBacktest(candles, strat, saveportfolio=True, plot=True)
        #bt.start()
        bt = CandlesBacktest(strat, "20160101", "20161231", saveportfolio=True, progressbar=True)
        #bt = FullCandlesBacktest(strat, saveportfolio=True, progressbar=True, candlesperc=0.05)

        profit = bt.start()
        print(instrument.name, profit)
        #    granularity = "VOL100"
        #    granularity = "S5"
        #    granularity = Granularity.M15


if __name__ == "__main__":
    main()
