import numpy as np
from progressbar import Bar, ETA, Percentage, ProgressBar

from jwoanda.backtests.backtest import Backtest
from jwoanda.enums import Granularity


class TicksBacktest(Backtest):
    def __init__(self, candles, strategy, **kwargs):
        super(TicksBacktest, self).__init__(strategy, **kwargs)
        self.candles = candles

    def start(self):

        #print(type(self.candles))
        #print(self.candles)
        candles = self.candles.data
        if self.showprogressbar:
            pbar = ProgressBar(widgets=['Backtesting: ',
                                        Percentage(),
                                        Bar(),
                                        ETA()],
                               maxval=len(candles)).start()

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
            granname = self.granularity.name if isinstance(self.granularity, Granularity) else self.granularity
            self.portfolio.save("BT-" + "-".join([self.strategy.name, self.instrument.name, granname, str(self.candles.year)]) + ".portfolio")

        #        print(self.portfolio.trades)
        trades = self.portfolio.trades
        #if not 'status' in trades.columns:
        #    return 0.
        #trades = trades[trades.status == ]

        pl = np.sum(trades["pl"])
        return pl
