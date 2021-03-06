#!/usr/bin/python

from __future__ import print_function

import logging
import sys

from jwoanda.strategies.random import RandomStrategy
from jwoanda.backtests.backtest import Backtest
from jwoanda.enums import VolumeGranularity, Granularity
from jwoanda.instenum import Instruments


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
        strat = RandomStrategy(instrument, granularity, units=1)
        bt = Backtest(strat, "20160101", "20161231", saveportfolio=True, progressbar=True)
        profit = bt.start()
        print(instrument.name, profit)

if __name__ == "__main__":
    main()
