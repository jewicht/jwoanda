import logging

from jwoanda.strategy import TickStrategy
from jwoanda.enums import ExitReason
from jwoanda.numpyfcn import tema

class TickEmaStrategy(TickStrategy):
    def __init__(self, instrument, **kwargs):
        super(TickEmaStrategy, self).__init__("TickEmaStrategy", instrument, **kwargs)
        ##self.invested = 0
        self.tradeId = -1
        self.smas = 0
        self.smal = 0
        self.longperiod = kwargs.get("longperiod", 0.2)
        self.shortperiod = kwargs.get("shortperiod", 0.3)

        self.emal = tema(self.longperiod)
        self.emas = tema(self.shortperiod)

        self.reqticks = 5


    def onTick(self, tick):
        instrument, time, bid, ask = tick

        emasvp = self.emas.prev
        emalvp = self.emal.prev

        emasv = self.emas.get(0.5*(bid+ask))
        emalv = self.emal.get(0.5*(bid+ask))

        logging.debug("emasv = %.5f emalv = %.5f",
                      emasv,
                      emalv)
        
        if (emasv > emalv) and (emasvp < emalvp):
            #go long, close short first
            #print("go long ", time, smashort, smalong)
            if self.tradeId > -1:
                self.closeposition(self.instrument,
                                   self.tradeId,
                                   ExitReason.NORMAL)

            self.tradeId = self.openposition(self.instrument,
                                             self.units,
                                             stoploss=self.stoploss,
                                             takeprofit=self.takeprofit)
            logging.debug("Open long = %d", self.tradeId)
            ##self.invested = +1
            return
        if (emasv < emalv) and (emasvp > emalvp):
            #go short, close long first
            #print("go short ", time, smashort, smalong)
            if self.tradeId > -1:
                self.closeposition(self.instrument,
                                   self.tradeId,
                                   ExitReason.NORMAL)

            self.tradeId = self.openposition(self.instrument,
                                             -self.units,
                                             stoploss=self.stoploss,
                                             takeprofit=self.takeprofit)
            logging.debug("Open short = %d", self.tradeId)
            ##self.invested = -1
            return

