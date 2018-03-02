#!/usr/bin/ipython -i

from __future__ import print_function

import logging
from datetime import datetime
import pathlib2

from jwoanda.strategies.random import RandomStrategy
from jwoanda.appbuilder import TradingAppThread
from jwoanda.enums import Granularity, VolumeGranularity
from jwoanda.instenum import Instruments


pathlib2.Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename='logs/trading_random-{}.log'.format(datetime.utcnow().strftime("%Y%m%d%H%M")),
                    level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s')

strategies = []

strategy = RandomStrategy((Instruments.GBP_USD, Granularity.S30), units=1, prob=1., stoploss=100, takeprofit=100)
strategies.append(strategy)

strategy = RandomStrategy((Instruments.EUR_USD, Granularity.M1), units=1, prob=1., stoploss=100, takeprofit=100)
strategies.append(strategy)


tab = TradingAppThread(strategies)
tab.start()
