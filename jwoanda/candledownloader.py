import threading
from datetime import datetime
import logging
from queue import Queue
import random

from jwoanda.history import downloadcandles
from jwoanda.instenum import Instruments
from jwoanda.history import RealHistoryManager
from jwoanda.enums import Granularity
from jwoanda.portfolio.oandaportfolio import OandaPortfolio
from jwoanda.enums import Events

def seconds_since_midnight():
    now = datetime.now()
    return (now - now.replace(hour=0,
                              minute=0,
                              second=0,
                              microsecond=0)).total_seconds()


class Clock(threading.Thread):

    def __init__(self, g, ev):
        super(Clock, self).__init__(name=["Clock", g.name])
        self.kill = False
        self.g = g
        self.stop = threading.Event()
        self.name = "_".join(["Clock", g.name])
        self.ev = ev


    def run(self):
        while not self.kill:
            ssm = seconds_since_midnight()
            timetowait = self.g.value - (ssm  % self.g.value)
            self.stop.wait(timetowait)
            if self.kill:
                return
            self.ev.set()
            logging.debug("%s %s", self.name, datetime.now())
            self.ev.clear()    


    def disconnect(self):
        self.kill = True
        self.stop.set()


class CandleDownloader(threading.Thread):

    def __init__(self, ilist, granularity, hm, portfolio, evc, evr):
        super(CandleDownloader, self).__init__(name='_'.join(["CandleDownloader", granularity.name] +
                                                             [i.name for i in ilist]))

        self.stop = threading.Event()
        self.kill = False
        self.ilist = ilist
        self.granularity = granularity
        self.hm = hm
        self.portfolio = portfolio

        self.evc = evc
        self.evr = evr


    def run(self):

        for instrument in self.ilist:
            candles = downloadcandles(instrument.name, self.granularity.name, 100)
            for candle in candles:
                if candle.complete:
                    self.hm.addCandle(instrument, self.granularity, candle)
        
        while not self.kill:
            self.evc.wait()
            if self.kill:
                return
            
            ssm = round(seconds_since_midnight())
            now = datetime.now()
            ts = int(now.strftime('%s'))
            logging.debug(now)
            logging.debug(ts)

            for instrument in self.ilist:
                if not self.portfolio.istradeable(instrument):
                    logging.debug("%s not tradeable", instrument.name)
                    continue

                success = False
                while not success:
                    candles = downloadcandles(instrument.name, self.granularity.name, 2)
                    for candle in candles:
                        if int(float(candle.time)) == ts - self.granularity.value:
                            logging.debug("We have the candle we are looking for")
                            if candle.complete == True:
                                logging.debug(candle)
                                logging.debug("It is complete")
                                success = True
                                self.hm.addCandle(instrument, self.granularity, candle)
                            else:
                                logging.debug("It is not complete")
                    if not success:
                        logging.debug("retry")
                        self.stop.wait(0.1 + 0.5*random.random())
            self.evr.set()
            self.evr.clear()
                    
    def disconnect(self):
        self.kill = True
        self.evc.set()
