import logging
import matplotlib.pyplot as plt
import numpy as np

from jwoanda.backtests.backtest import Backtest
from jwoanda.strategy import Strategy

class SimpleBacktest(Backtest):
    def __init__(self, candles, strategy, **kwargs):
        super(SimpleBacktest, self).__init__(strategy, **kwargs)

        if not isinstance(self.strategy, Strategy):
            raise Exception("Not a single-candle strategy")

        self.candles = candles

        self.longcut = kwargs.get("longcut", 0.)
        self.shortcut = kwargs.get("shortcut", 0.)

        self.doplot = kwargs.get("plot", False)
        logging.info("SimpleBacktest: long > %f, short < %f",
                     self.longcut,
                     self.shortcut)


    @property
    def instrument(self):
        return self.strategy.instrument      


    def start(self):
        candles = self.candles.data
        closeMed = 0.5 * (candles['closeAsk'] + candles['closeBid'])

        pip = self.instrument.pip
        
        returns = np.append(np.diff(closeMed, n=1), [0.]) / pip
        #        returns = np.insert(np.diff(closeMed, n=1), 0, 0.) / pip

        spread = (candles["closeAsk"] - candles["closeBid"] + candles["openAsk"] - candles["openBid"])/2.

        meanspread = spread.mean()
        
        self.strategy.modeBT = True
        self.strategy.calcIndicators(candles)
        self.strategy.calcMVA()


        if not hasattr(self.strategy, 'indicators'):
            logging.error("No indicators in strategy")
            return (0., 0)

        longpos = 1 * (self.strategy.indicators[:, -1] > self.longcut)
        shortpos = -1 * (self.strategy.indicators[:, -1] < self.shortcut)

        allpos = longpos + shortpos
        
        longprof = longpos * returns
        shortprof = shortpos * returns
        prof = allpos * returns

        
        #compute number of trades
        ntrades = len(np.where(np.diff(np.signbit(allpos)))[0])

        profit = np.sum(prof)

        if self.doplot:
            f, ax = plt.subplots(3, sharex=True)
            ax[0].plot(np.cumsum(longprof))
            ax[0].set_title('long')
            ax[1].plot(np.cumsum(shortprof))
            ax[1].set_title('short')
            ax[2].plot(np.cumsum(prof))
            ax[2].set_title('long+short')
            plt.show()

        return profit, ntrades

