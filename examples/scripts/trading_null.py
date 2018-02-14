#!/usr/bin/ipython -i

from __future__ import print_function

import logging
import threading
from datetime import datetime
import pathlib

from jwoanda.strategies.null import NullStrategy, NullMultiStrategy
from jwoanda.appbuilder import TradingAppThread
from jwoanda.enums import Granularity, VolumeGranularity
from jwoanda.instenum import Instruments


def findtab():
    tab = filter(lambda x: 'TradingApp' in x.name, threading.enumerate())
    return tab[0]


pathlib.Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename='logs/trading_null-{}.log'.format(datetime.utcnow().strftime("%Y%m%d%H%M")),
                    level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s')

strategies = []

strategy = NullMultiStrategy([(Instruments.GBP_USD, Granularity.S30),
                              (Instruments.EUR_GBP, Granularity.S30)],
                             units=1,
                             takeprofit=30,
                             stoploss=30,
                             longprob=0.4,
                             shortprob=0.4)
strategies.append(strategy)

# for instrument in Instruments:
#     strategy = NullStrategy(instrument, VolumeGranularity(20))
#     strategies.append(strategy)

strategy = NullStrategy([(Instruments.EUR_USD,
                          VolumeGranularity(20))]
                        units=1,
                        takeprofit=30,
                        stoploss=30,
                        longprob=0.4,
                        shortprob=0.4)
strategies.append(strategy)

tab = TradingAppThread(strategies, usemp=False, usefakedata=False)
tab.start()
