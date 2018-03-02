from __future__ import print_function

try:
    from queue import Queue
except:
    from Queue import Queue
import threading
from time import sleep
import logging
import signal

from jwoanda.oandaaccount import oandaenv
from jwoanda.datastreamers import RatesStreamer, FakeRatesStreamer, TransactionsStreamer, HeartbeatCheck
from jwoanda.strategy import BaseStrategy, Strategy, TickStrategy
from jwoanda.portfolio.portfolio import Portfolio
from jwoanda.portfolio.oandaportfolio import OandaPortfolio, OandaPortfolioManager, OandaPortfolioProxy
from jwoanda.enums import Events, ExitReason
from jwoanda.strategytrading import StrategyTrading, TickStrategyTrading
from jwoanda.candledownloader import CandleDownloader, Clock
from jwoanda.history import RealHistoryManager
from jwoanda.utils import get_items

class TradingAppThread(threading.Thread):
    def __init__(self, strategies, environment='practice', **kwargs):
        super(TradingAppThread, self).__init__(name='TradingAppThread')
        self.ta = TradingApp(strategies, environment=environment, nosignal=True, **kwargs)

    def run(self):
        self.ta.run()

    def disconnect(self):
        self.ta.disconnect()



class TradingApp(object):

    def __init__(self, strategies, environment='practice', **kwargs):

        self.strategies = strategies
        self.portfolio = OandaPortfolio()
        
        self.doterminate = False
        if not kwargs.get("nosignal", False):
            signal.signal(signal.SIGTERM, self.signal_term_handler)
            signal.signal(signal.SIGINT, self.signal_term_handler)

        self.usegtk = bool(kwargs.get("usegtk", False))
        self.usefakedata = bool(kwargs.get("usefakedata", False))
        self.closepositions = bool(kwargs.get("closepositions", True))

        if not isinstance(self.portfolio, Portfolio):
            raise ValueError("Not a portfolio?")

        tradedinstruments = set()
        for strategy in self.strategies:
            if not isinstance(strategy, BaseStrategy):
                raise ValueError("Not a strategy?")
            for instrument in strategy.instruments:
                tradedinstruments.add(instrument.name)

        logging.info("tradedinstruments = %s", " ".join(tradedinstruments))


        tickQueues = []

        self.threads = []
        self.processes = []
        pipelist = []

        if self.usegtk:
            from jwoanda.gtkinterface import GTKInterface
            self.gtkinterface = GTKInterface(tradedinstruments, name="GTKInterface")
            self.threads.append(self.gtkinterface)
        else:
            self.gtkinterface = None

        iglist = set()
        glist = set()
        for strategy in strategies:
            for ig in strategy.iglist:
                i, g = ig
                iglist.add(ig)
                glist.add(g)

        clocks = []

        candleCloseEvents = {}
        candleReadyEvents = {}
        for g in glist:
            ev = threading.Event()
            clock = Clock(g, ev)
            self.threads.append(clock)

            clocks.append( {'clock': clock,
                            'g': g,
                            'ev' : ev})
            candleCloseEvents[g] = ev
            candleReadyEvents[g] = threading.Event()
            
        self.hm = RealHistoryManager(iglist)

        
        for strategy in self.strategies:
            eQ = Queue()
            tickQueues.append({'iglist': strategy.iglist,
                               'queue': eQ})
            
            strategy.portfolio = self.portfolio
            strategy.hm = self.hm
            
            tst = TickStrategyTrading(strategy, eQ)
            self.threads.append(tst)
            
            if isinstance(strategy, Strategy):
                st = StrategyTrading(strategy, candleReadyEvents[strategy.granularity])
                self.threads.append(st)
                
        
        for g in glist:
            ilist = set()
            for strategy in self.strategies:
                for i, gg in strategy.iglist:
                    if g == gg:
                        ilist.add(i)

            evc = candleCloseEvents[g]
            evr = candleReadyEvents[g]
            cdth = CandleDownloader(ilist, g, self.hm, self.portfolio, evc, evr)
            self.threads.append(cdth)
            


        est = TransactionsStreamer(self.portfolio, name="TransactionsStreamer")
        self.threads.append(est)

        eshb = HeartbeatCheck(est, 'lastheartbeattime',
                              name='HeartbeatCheck-TransactionsStreamer',
                              delay=5)
        self.threads.append(eshb)

        if self.usefakedata:
            rst = FakeRatesStreamer(tickQueues,
                                    tradedinstruments,
                                    [self.portfolio],
                                    name="RateStreamer")
            self.threads.append(rst)
        else:
            rst = RatesStreamer(tickQueues,
                                tradedinstruments,
                                [self.portfolio],
                                self.gtkinterface,
                                name="RateStreamer")
            self.threads.append(rst)

        rshb1 = HeartbeatCheck(rst, 'lastheartbeattime', name='HeartbeatCheck-RateStreamer', delay=5)
        self.threads.append(rshb1)
        rshb2 = HeartbeatCheck(rst, 'lastpricetime', name='PriceCheck-RateStreamer', delay=60)
        self.threads.append(rshb2)
        self.tickQueues = tickQueues
        self.candleCloseEvents = candleCloseEvents
        self.candleReadyEvents = candleReadyEvents


    def run(self):
        # start threads
        for t in self.threads:
            logging.info("Starting thread %s", t.name)
            t.start()

        # start processes
        for p in self.processes:
            logging.info("Starting process %s", p.name)
            p.start()

        # Wait for all threads to complete
        while not self.doterminate:
            sleep(1)
            for t in self.threads:
                if not t.isAlive():
                    msg = "Thread %s died, exiting..." % t.name
                    logging.error(msg)
                    oandaenv.sendemail(msg, '')
                    self.doterminate = True

            for p in self.processes:
                if not p.is_alive():
                    msg = "Process %s died, exiting..." % p.name
                    logging.error(msg)
                    oandaenv.sendemail(msg, '')
                    self.doterminate = True


        logging.info("Exiting Main Thread")

        logging.info("Sending disconnect signals to all threads and processes")
        for t in self.threads:
            t.disconnect()

        for p in self.processes:
            p.disconnect()
        
        sleep(1)

        if len(self.processes) > 0:
            logging.info("Sending terminate signals to all processes")
            for p in self.processes:
                logging.info("Process %s : alive = %d", p.name, p.is_alive())
                p.terminate()

        logging.info("Closing all position")

        if self.closepositions:
            self.portfolio.closeallpositions(ExitReason.END)

        logging.info("Saving portfolio")
        self.portfolio.save()


    def disconnect(self):
        self.doterminate = True


    def signal_term_handler(self, signal, frame):
        logging.info("Caught SIGINT/SIGTERM, exiting")
        self.doterminate = True
