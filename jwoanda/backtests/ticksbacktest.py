import numpy as np
from progressbar import Bar, ETA, Percentage, ProgressBar

from jwoanda.backtests.backtest import BaseBacktest
from jwoanda.enums import Granularity
from jwoanda.history import getcandles

class TicksBacktest(BaseBacktest):
    def __init__(self, strategy, start, end, **kwargs):
        super(TicksBacktest, self).__init__(strategy, start, end, **kwargs)
        self.candles = getcandles(strategy.instrument, Granularity.S5, start, end)


    def start(self):
        candles = self.candles.data
        if self.showprogressbar:
            pbar = ProgressBar(widgets=['Backtesting: ',
                                        Percentage(),
                                        Bar(),
                                        ETA()],
                               max_value=len(candles)).start()

        for cnt, candle in enumerate(candles):

            self.simpletickgenerator(candle, self.strategy.instrument)
            
            if self.showprogressbar:
                pbar.update(cnt)

        if self.showprogressbar:
            pbar.finish()

        if self.saveportfolio:
            self.save()

        trades = self.portfolio.trades
        pl = np.sum(trades["pl"])
        return pl, self.portfolio.ntrades
