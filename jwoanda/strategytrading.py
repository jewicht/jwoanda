import logging

from abc import ABCMeta, abstractmethod
from six import with_metaclass

from jwoanda.enums import Events
from jwoanda.strategy import MultiStrategy, TickStrategy


class BaseStrategyTrading(with_metaclass(ABCMeta)):
    def __init__(self, strategy, cmt, **kwargs):
        self.strategy = strategy
        self.cmt = cmt


    @abstractmethod
    def tickEvent(self):
        pass


    @abstractmethod
    def candleEvent(self):
        pass
    

    
class StrategyTrading(BaseStrategyTrading):
    def __init__(self, strategy, cmt, **kwargs):
        super(StrategyTrading, self).__init__(strategy, cmt)


    def tickEvent(self):
        mcandles = self.cmt.mcandles
        ncandles = mcandles.ncandles
        reqcandles = self.strategy.reqcandles
        mincandles = self.strategy.mincandles

        candles = mcandles.tail(reqcandles, oneincomplete=1)
        ocandles = candles[self.strategy.instrument].data.view()
        ocandles.flags.writeable = False
        try:
            self.strategy.onTick(ocandles, ocandles.size - 1)
        except:
            logging.exception("your strategy crashed in onTick")


    def candleEvent(self):
        candles = self.cmt.mcandles.candles(self.strategy.instrument)
        
        ncandles = candles.ncandles
        reqcandles = self.strategy.reqcandles
        mincandles = self.strategy.mincandles
        
        #logging.debug("ncandles = {} reqcandles = {} mincandles = {}".format(ncandles, reqcandles, mincandles))
        if mincandles > ncandles -1:
            return
        tcandles = candles.tail(reqcandles)
        size = tcandles.data.size
        ocandles = tcandles.data.view()
        ocandles.flags.writeable = False
        try:
            self.strategy.onCandle(ocandles, ocandles.size - 1)
        except:
            logging.exception("your strategy crashed in onCandle")



class MultiStrategyTrading(BaseStrategyTrading):
    def __init__(self, strategy, cmt, **kwargs):
        super(MultiStrategyTrading, self).__init__(strategy, cmt)


    def tickEvent(self):
        pass


    def candleEvent(self):
        mcandles = self.cmt.mcandles
        ncandles = mcandles.ncandles
        reqcandles = self.strategy.reqcandles
        mincandles = self.strategy.mincandles

        #logging.debug("ncandles = {} reqcandles = {} mincandles = {}".format(ncandles, reqcandles, mincandles))
        if mincandles > ncandles -1:
            return
        candles = mcandles.tail(reqcandles)
        size = candles[self.strategy.instruments[0]].data.size

        cdict = {}
        for instrument in self.strategy.instruments:
            cc = candles[instrument].data.view()
            cc.flags.writeable = False
            cdict[instrument] = cc
        try:
            self.strategy.onMultiCandle(cdict, size - 1)
        except:
            logging.exception("your strategy crashed in onMultiCandle")



class TickStrategyTrading(BaseStrategyTrading):
    def __init__(self, strategy, cmt, **kwargs):
        super(TickStrategyTrading, self).__init__(strategy, cmt)


    def tickEvent(self, tick):
        try:
            self.strategy.onTick(tick)
        except:
            pass


    def candleEvent(self):
        pass
