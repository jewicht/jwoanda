import logging
from datetime import datetime

from jwoanda.strategy import Strategy
from jwoanda.history import floattostr

class NullStrategy(Strategy):
    def __init__(self, iglist, **kwargs):
        super(NullStrategy, self).__init__("NullStrategy",
                                           iglist,
                                           **kwargs)

    def onTick(self, tick):
        instrument, t, b, a = tick
        logging.info("onTick instrument=%s time=%s bid=%s ask=%s",
                     instrument.name,
                     datetime.fromtimestamp(t),
                     floattostr(b, instrument.displayPrecision),
                     floattostr(a, instrument.displayPrecision))


    def onCandle(self):
        for instrument, granularity in self.iglist:
            candles = self.getcandles(instrument, granularity, 1)
            if candles is None:
                return
            lastcandle = candles[0]
            logging.info("onCandle instrument=%s, time=%s, open=%s, high=%s, low=%s, close=%s, volume=%s",
                         instrument.name,
                         datetime.fromtimestamp(lastcandle['time']),
                         floattostr(lastcandle['openAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['highAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['lowAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['closeAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['volume'], 0))
        return

