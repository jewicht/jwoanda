import logging
from datetime import datetime

from jwoanda.strategy import Strategy
from jwoanda.history import floattostr

class NullStrategy(Strategy):
    def __init__(self, iglist, **kwargs):
        super(NullStrategy, self).__init__("NullStrategy",
                                           iglist,
                                           **kwargs)

    def onTick(self):
        return
        lastcandle = candles[cnt]
        logging.info("onTick instrument=%s, time=%s, open=%s, high=%s, low=%s, close=%s, volume=%s",
                     self.instrument.name,
                     datetime.fromtimestamp(lastcandle['time']),
                     floattostr(lastcandle['openAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['highAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['lowAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['closeAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['volume'], 0))

        return


    def onCandle(self):
        candles = self.getcandles(self.instrument, self.granularity, 1)
        if candles is None:
            return
        lastcandle = candles[0]
        logging.info("onCandle instrument=%s, time=%s, open=%s, high=%s, low=%s, close=%s, volume=%s",
                     self.instrument.name,
                     datetime.fromtimestamp(lastcandle['time']),
                     floattostr(lastcandle['openAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['highAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['lowAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['closeAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['volume'], 0))
        return




class NullMultiStrategy(Strategy):
    def __init__(self, iglist, **kwargs):
        super(NullMultiStrategy, self).__init__("MultiNullStrategy",
                                                iglist,
                                                **kwargs)

    def onCandle(self):
        for i, g in self.iglist:
            lastcandle = self.getcandles(i, g, 1)
            if lastcandle is None:
                continue
            lastcandle = lastcandle[0]
            logging.info("onCandle instrument=%s, time=%s, open=%s, high=%s, low=%s, close=%s, volume=%s",
                         instrument.name,
                         datetime.fromtimestamp(lastcandle['time']),
                         floattostr(lastcandle['openAsk'], i.displayPrecision),
                         floattostr(lastcandle['highAsk'], i.displayPrecision),
                         floattostr(lastcandle['lowAsk'], i.displayPrecision),
                         floattostr(lastcandle['closeAsk'], i.displayPrecision),
                         floattostr(lastcandle['volume'], 0))
        return

