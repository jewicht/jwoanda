#!/usr/bin/ipython -i

from __future__ import print_function

import logging
from datetime import datetime
import pathlib2

from jwoanda.strategies.tickema import TickEmaStrategy
from jwoanda.appbuilder import TradingAppThread
from jwoanda.enums import Granularity, VolumeGranularity
from jwoanda.instenum import Instruments


pathlib2.Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename='logs/trading_tick-{}.log'.format(datetime.utcnow().strftime("%Y%m%d%H%M")),
                    level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s')
 
strategies = []

strategy = TickEmaStrategy(Instruments.GBP_USD, units=1)
strategies.append(strategy)

strategy = TickEmaStrategy(Instruments.EUR_USD, units=1)
strategies.append(strategy)

tab = TradingAppThread(strategies)
tab.start()
