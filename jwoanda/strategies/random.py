import numpy as np
import logging

from jwoanda.strategy import Strategy
from jwoanda.enums import ExitReason

class RandomStrategy(Strategy):
    def __init__(self, instruments, granularity, **kwargs):
        super(RandomStrategy, self).__init__("RandomStrategy", instruments, granularity, **kwargs)
        self.prob = kwargs.get("prob", 0.5)
        self.state = 0
        self.tradeId = -1
        
    def onTick(self, tick):
        pass

    def onCandle(self):
        logging.debug("state = %d tradeId = %d", self.state, self.tradeId)
        
        if np.random.random() > self.prob:
            return

        
        if self.state == 0:
            if np.random.random() > 0.5:
                self.state = +1
            else:
                self.state = -1
        else:
            self.state = 0

        if self.state == +1:
            if self.tradeId > -1:
                return
            logging.debug("try to open long position")
            self.tradeId = self.openposition(self.instrument,
                                             self.units,
                                             stoploss=self.stoploss,
                                             takeprofit=self.takeprofit)
            if self.tradeId < 0:
                self.state = 0
            
            return

        if self.state == 0:
            if self.tradeId < 0:
                return
            logging.debug("try to close position")
            self.closeposition(self.instrument,
                               self.tradeId,
                               ExitReason.NORMAL)
            self.tradeId = -1
            return

        if self.state == -1:
            if self.tradeId > -1:
                return
            logging.debug("try to open short position")
            self.tradeId = self.openposition(self.instrument,
                                             -self.units,
                                             stoploss=self.stoploss,
                                             takeprofit=self.takeprofit)

            if self.tradeId < 0:
                self.state = 0
