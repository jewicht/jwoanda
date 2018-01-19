import numpy as np
from progressbar import Bar, ETA, Percentage, ProgressBar

from jwoanda.backtests.backtest import Backtest
from jwoanda.enums import Granularity
from jwoanda.history import HistoryManager

class TicksBacktest(Backtest):
    def __init__(self, strategy, start, end, **kwargs):
        super(TicksBacktest, self).__init__(strategy, start, end, **kwargs)
        self.candles = HistoryManager.getcandles(strategy.instrument, Granularity.S5, start, end)
        
    def start(self):

        #print(type(self.candles))
        #print(self.candles)
        candles = self.candles.data
        if self.showprogressbar:
            pbar = ProgressBar(widgets=['Backtesting: ',
                                        Percentage(),
                                        Bar(),
                                        ETA()],
                               max_value=len(candles)).start()

        self.strategy.modeBT = True
        self.strategy.calcIndicators(candles)
        self.strategy.calcMVA()

        for i in range(self.strategy.reqcandles, candles.size):

            self.tickgenerator(candles[i], self.strategy.instrument)
            
            if self.showprogressbar:
                pbar.update(i+1)

        if self.showprogressbar:
            pbar.finish()

        if self.saveportfolio:
            self.save()

        trades = self.portfolio.trades
        pl = np.sum(trades["pl"])
        return pl, self.portfolio.ntrades
