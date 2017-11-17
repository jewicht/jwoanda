from __future__ import print_function

try:
    from queue import Queue as thQueue
except:
    from Queue import Queue as thQueue
import threading
from multiprocessing import Queue as mpQueue, Pipe
from time import sleep
import logging
import signal

from jwoanda.oandaaccount import oandaenv
from jwoanda.candlemaker import CandleMakerHelperThread, CandleMakerHelperProcess
from jwoanda.datastreamers import RatesStreamer, FakeRatesStreamer, TransactionsStreamer, HeartbeatCheck
from jwoanda.strategy import BaseStrategy
from jwoanda.portfolio.portfolio import Portfolio
from jwoanda.portfolio.oandaportfolio import OandaPortfolio, OandaPortfolioManager, OandaPortfolioProxy
from jwoanda.enums import Events, ExitReason
from jwoanda.gtkinterface import GTKInterface


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

        self.usemp = bool(kwargs.get("usemp", False))
        self.usegtk = bool(kwargs.get("usegtk", False))
        self.usefakedata = bool(kwargs.get("usefakedata", False))
        self.closepositions = bool(kwargs.get("closepositions", True))

        if not isinstance(self.portfolio, Portfolio):
            raise ValueError("Not a portfolio?")

        tradedinstruments = []
        for strategy in self.strategies:
            if not isinstance(strategy, BaseStrategy):
                raise ValueError("Not a strategy?")

            for instrument in strategy.instruments:
                if instrument in tradedinstruments:
                    continue
                tradedinstruments.append(instrument.name)
        logging.info("tradedinstruments = %s", " ".join(tradedinstruments))


        tickQueues = {}
        #tickQueues go from RateStreamer (1) to CandleMaker ( size(strategies) )

        self.threads = []
        self.processes = []
        pipelist = []

        if self.usemp:
            self.trigger = thQueue()

        if self.usegtk:
            self.gtkinterface = GTKInterface(tradedinstruments, name="GTKInterface")
            self.threads.append(self.gtkinterface)
        else:
            self.gtkinterface = None

        for strategy in self.strategies:
            #instruments = '-'.join([instr.name for instr in strategy.instruments])
            if self.usemp:

                tQ = mpQueue()
                tickQueues[tuple(strategy.instruments)] = tQ

                #replace portfolio:
                pipea, pipeb = Pipe()
                pipelist.append(pipea)
                newport = OandaPortfolioProxy(self.trigger, pipeb)
                strategy.portfolio = newport

                cmhp = CandleMakerHelperProcess(tQ,
                                                strategy,
                                                name='_'.join(["CandleMakerHelper", strategy.name]))
                self.processes.append(cmhp)
            else:
                tQ = thQueue()
                tickQueues[tuple(strategy.instruments)] = tQ

                strategy.portfolio = self.portfolio

                cmht = CandleMakerHelperThread(tQ,
                                               strategy,
                                               name='_'.join(["CandleMakerHelper", strategy.name]))
                self.threads.append(cmht)



        if self.usemp:
            opmt = OandaPortfolioManager(self.portfolio, self.trigger, pipelist)
            self.threads.append(opmt)

        est = TransactionsStreamer(self.portfolio, name="TransactionsStreamer")
        self.threads.append(est)

        eshb = HeartbeatCheck(est, 'lastheartbeattime', name='HeartbeatCheck-TransactionsStreamer', delay=5)
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

        if self.usemp:
            self.trigger.put(Events.KILL)

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
