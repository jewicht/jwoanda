import logging

from jwoanda.strategy import Strategy
from jwoanda.enums import ExitReason
import talib as ta
import numpy as np

class TwoSMAsStrategy(Strategy):
    def __init__(self, iglist, **kwargs):
        super(TwoSMAsStrategy, self).__init__("TwoSMAsStrategy", iglist, **kwargs)
        ##self.invested = 0
        self.tradeId = -1
        self.smas = 0
        self.smal = 0
        self.options['longperiod'] = kwargs.get("longperiod", 20)
        self.options['shortperiod'] = kwargs.get("shortperiod", 10)

        self.modeBT = False
        self.options['matype'] = kwargs.get('matype', ta.MA_Type.SMA)
        
        logging.info("     longperiod = %d, shortperiod = %d, matype = %d",
                     self.options['longperiod'],
                     self.options['shortperiod'],
                     self.options['matype'])
        

    def calcIndicators(self, candles):
        self.indicators = np.empty([candles.size, 3])
        self.smas = ta.MA(candles['closeBid'], timeperiod=int(self.options['shortperiod']), matype=self.options['matype'])
        self.smal = ta.MA(candles['closeBid'], timeperiod=int(self.options['longperiod']), matype=self.options['matype'])
        self.rsi = ta.RSI(candles['closeBid'], timeperiod=int(self.options['longperiod']))
        
        self.mva = self.smas - self.smal
        self.indicators[:, 0] = self.smas
        self.indicators[:, 1] = self.smal
        self.indicators[:, 2] = self.mva


    def onTick(self):
        pass


    def onCandle(self):

        candles = self.getcandles(self.instrument, self.granularity, self.options['longperiod'] + 2)

        if candles is None:
            return
        
        lastcandle = candles[-1]
        closeBid = lastcandle['closeBid']
        closeAsk = lastcandle['closeAsk']
        time = lastcandle['time']

        self.calcIndicators(candles)
            
        smashortprev = self.smal[-2]
        smashort = self.smal[-1]

        smalongprev = self.smas[-2]
        smalong = self.smas[-1]
        rsi = self.rsi[-1]
        

        if (smashort > smalong) and (smashortprev < smalongprev) and (rsi < 0.25):
            #go long, close short first
            #print("go long ", time, smashort, smalong)
            if self.tradeId > -1:
                self.closeposition(self.instrument,
                                   self.tradeId,
                                   ExitReason.NORMAL)

                self.tradeId = self.openposition(self.instrument,
                                                 self.units)

            logging.debug("Open long = %d", self.tradeId)
            ##self.invested = +1
            return
        if (smashort < smalong) and (smashortprev > smalongprev) and (rsi > 0.75):
            #go short, close long first
            #print("go short ", time, smashort, smalong)
            if self.tradeId > -1:
                self.closeposition(self.instrument,
                                   self.tradeId,
                                   ExitReason.NORMAL)
            self.tradeId = self.openposition(self.instrument,
                                             -self.units)

            logging.debug("Open short = %d", self.tradeId)
            ##self.invested = -1
            return
