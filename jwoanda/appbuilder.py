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

        self.doterminate = False
        if not kwargs.get("nosignal", False):
            signal.signal(signal.SIGTERM, self.signal_term_handler)
            signal.signal(signal.SIGINT, self.signal_term_handler)

        self.usegtk = bool(kwargs.get("usegtk", False))
        self.usefakedata = bool(kwargs.get("usefakedata", False))
        self.closepositions = bool(kwargs.get("closepositions", True))
        self.docheckTPSL = bool(kwargs.get("docheckTPSL", True))


        self.strategies = strategies
        self.portfolio = OandaPortfolio(docheckTPSL=self.docheckTPSL)

        if not isinstance(self.portfolio, Portfolio):
            raise ValueError("Not a portfolio?")

        self.tradedinstruments = set()
        for strategy in self.strategies:
            if not isinstance(strategy, BaseStrategy):
                raise ValueError("Not a strategy?")
            for instrument in strategy.instruments:
                self.tradedinstruments.add(instrument)

        logging.info("tradedinstruments = %s", " ".join([i.name for i in self.tradedinstruments]))


        self.threads = []
        self.processes = []

        if self.usegtk:
            from jwoanda.gtkinterface import GTKInterface
            self.gtkinterface = GTKInterface(self.tradedinstruments, name="GTKInterface")
            self.threads.append(self.gtkinterface)
        else:
            self.gtkinterface = None

        self.iglist = set()
        self.glist = set()
        for strategy in strategies:
            self.glist.add(strategy.granularity)
            for i in strategy.instruments:
                self.iglist.add((i, strategy.granularity))

        self.tickQueues = []
        self.candleCloseEvents = {}
        self.candleReadyEvents = {}
        self.clocks = {}
        self.candledl = {}
        for g in self.glist:
            self.addClock(g)
            
        self.hm = RealHistoryManager(self.iglist)

        
        for strategy in self.strategies:
            tQ = Queue()
            self.tickQueues.append({'instruments': strategy.instruments,
                               'queue': tQ})
            
            strategy.portfolio = self.portfolio
            strategy.hm = self.hm
            
            tst = TickStrategyTrading(strategy, tQ)
            self.threads.append(tst)
            
            if isinstance(strategy, Strategy):
                st = StrategyTrading(strategy, self.candleReadyEvents[strategy.granularity])
                self.threads.append(st)

        
        for g in self.glist:
            ilist = set()
            for strategy in self.strategies:
                if strategy.granularity == g:
                    for i in strategy.instruments:
                        ilist.add(i)
        
            self.addCandleDL(ilist, g)

        est = TransactionsStreamer(self.portfolio)
        self.threads.append(est)

        eshb = HeartbeatCheck(est, 'lastheartbeattime',
                              name='HeartbeatCheck-TransactionsStreamer',
                              delay=5)
        self.threads.append(eshb)

        if self.usefakedata:
            self.rst = FakeRatesStreamer(self.tickQueues,
                                        self.tradedinstruments,
                                        self.portfolio)
            self.threads.append(self.rst)
        else:
            self.rst = RatesStreamer(self.tickQueues,
                                self.tradedinstruments,
                                self.portfolio,
                                self.gtkinterface,
                                docheckTPSL=self.docheckTPSL)
            self.threads.append(self.rst)

        rshb1 = HeartbeatCheck(self.rst, 'lastheartbeattime', name='HeartbeatCheck-RateStreamer', delay=5)
        self.threads.append(rshb1)
        rshb2 = HeartbeatCheck(self.rst, 'lastpricetime', name='PriceCheck-RateStreamer', delay=60)
        self.threads.append(rshb2)

        #for s in strategies:
        #    self.addStrategy(s)

    def addCandleDL(self, ilist, g, start=False):
        evc = self.candleCloseEvents[g]
        evr = self.candleReadyEvents[g]
        cdth = CandleDownloader(ilist, g, self.hm, self.portfolio, evc, evr)
        if start:
            cdth.start()
        self.candledl[g] = cdth
        self.threads.append(cdth)
    

    def addStrategy(self, strategy, start=False):
        for i in strategy.instruments:
            self.hm.add(i, strategy.granularity)

        if not strategy.granularity in self.glist:
            # need to create clock and CandleDl
            self.addClock(strategy.granularity, start=start)
            self.addCandleDL(strategy.instruments, strategy.granularity, start=start)
            self.glist.add(strategy.granularity)
        else:
            cdl = self.candledl[strategy.granularity]
            for instrument in strategy.instruments:
                cdl.addInstrument(instrument)


        for instrument in strategy.instruments:
            self.hm.add(instrument, strategy.granularity)
            if not instrument in self.tradedinstruments:
                self.tradedinstruments.add(instrument)
                self.rst.addInstrument(instrument)

        tQ = Queue()
        self.tickQueues.append({'instruments': strategy.instruments,
                               'queue': tQ})

        tst = TickStrategyTrading(strategy, tQ)
        if start:
            tst.start()
        self.threads.append(tst)
        self.rst.setTickQueues(self.tickQueues)

        if isinstance(strategy, Strategy):
            st = StrategyTrading(strategy, self.candleReadyEvents[strategy.granularity])
            if start:
                st.start()
            self.threads.append(st)


    def addClock(self, g, start=False):
        ev = threading.Event()
        clock = Clock(g, ev)
        if start:
            clock.start()
        self.threads.append(clock)

        self.clocks[g] = clock
        self.candleCloseEvents[g] = ev
        self.candleReadyEvents[g] = threading.Event()


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
