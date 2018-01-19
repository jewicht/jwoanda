import logging
from datetime import datetime

from jwoanda.strategy import Strategy, MultiInstrumentsStrategy
from jwoanda.history import floattostr

class NullStrategy(Strategy):
    def __init__(self, instrument, granularity, **kwargs):
        super(NullStrategy, self).__init__("NullStrategy",
                                           instrument,
                                           granularity,
                                           **kwargs)

    def onTick(self, candles, cnt):
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


    def onCandle(self, candles, cnt):
        lastcandle = candles[cnt]
        logging.info("onCandle instrument=%s, time=%s, open=%s, high=%s, low=%s, close=%s, volume=%s",
                     self.instrument.name,
                     datetime.fromtimestamp(lastcandle['time']),
                     floattostr(lastcandle['openAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['highAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['lowAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['closeAsk'], self.instrument.displayPrecision),
                     floattostr(lastcandle['volume'], 0))
        return




class NullMultiStrategy(MultiInstrumentsStrategy):
    def __init__(self, instruments, granularity, **kwargs):
        super(NullMultiStrategy, self).__init__("MultiNullStrategy",
                                                instruments,
                                                granularity,
                                                **kwargs)

    def onMultiCandle(self, candles, cnt):
        for instrument in self.instruments:
            lastcandle = candles[instrument][cnt]
            logging.info("onMultiCandle instrument=%s, time=%s, open=%s, high=%s, low=%s, close=%s, volume=%s",
                         instrument.name,
                         datetime.fromtimestamp(lastcandle['time']),
                         floattostr(lastcandle['openAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['highAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['lowAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['closeAsk'], instrument.displayPrecision),
                         floattostr(lastcandle['volume'], 0))
        return

