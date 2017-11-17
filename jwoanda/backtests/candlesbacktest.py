import logging
import numpy as np
from progressbar import Bar, ETA, Percentage, ProgressBar

from jwoanda.backtests.backtest import Backtest
from jwoanda.strategy import Strategy
from jwoanda.oandaaccount import oandaenv
try:
    range = xrange
except:
    pass

class CandlesBacktest(Backtest):
    def __init__(self, candles, strategy, **kwargs):
        super(CandlesBacktest, self).__init__(strategy, **kwargs)

        self.candles = candles
        
        if not isinstance(self.strategy, Strategy):
            raise Exception("Not a strategy")

        logging.info("init CandlesBacktest for strategy %s", strategy.name)


    @property
    def instrument(self):
        return self.strategy.instrument      


    def start(self):
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
        instrument = self.strategy.instrument

        for i, candle in enumerate(candles):

            #self.simpletickgenerator(candle, instrument)
            self.randomtickgenerator(candle, instrument)

            #update price
            self.portfolio.setprice(instrument, (candle['time'], candle['closeBid'], candle['closeAsk']))
            
            self.strategy.onCandle(candles, i)

            if self.showprogressbar:
                pbar.update(i+1)

        if self.showprogressbar:
            pbar.finish()

        if self.saveportfolio:
            self.save()

        trades = self.portfolio.trades
        pl = np.sum(trades["pl"])

        return pl, self.portfolio.ntrades
