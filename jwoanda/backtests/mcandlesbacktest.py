import numpy as np
from progressbar import Bar, ETA, Percentage, ProgressBar


from jwoanda.backtests.backtest import Backtest
from jwoanda.strategy import MultiInstrumentsStrategy
from jwoanda.history import HistoryManager


class MCandlesBacktest(Backtest):
    def __init__(self, strategy, start, end, **kwargs):
        super(MCandlesBacktest, self).__init__(strategy, start, end, **kwargs)
        if not isinstance(self.strategy, MultiInstrumentsStrategy):
            raise Exception("Not a valid strategy")
        self.candles = HistoryManager.getmulticandles(strategy.instruments, strategy.granularity, start, end)

    @property
    def instruments(self):
        return self.strategy.instruments      

    def start(self):
        if self.showprogressbar:
            pbar = ProgressBar(widgets=['Backtesting: ',
                                        Percentage(),
                                        Bar(),
                                        ETA()],
                               max_value=self.candles.ncandles).start()

        mcandlesdict = {}
        for instrument in self.candles.instruments:
            mcandlesdict[instrument] = self.candles.candles(instrument).data
        
        for i in range(self.strategy.reqcandles, self.candles.ncandles):

            for instrument in self.candles.instruments:
                thiscandle = self.candles.candles(instrument).data[i]
                self.simpletickgenerator(thiscandle, instrument)

            #update price
            for instrument in self.candles.instruments:
                thiscandle = self.candles.candles(instrument).data[i]
                self.portfolio.setprice(instrument, (thiscandle['time'], thiscandle['closeBid'], thiscandle['closeAsk']))

            self.strategy.onMultiCandle(mcandlesdict, i)

            if self.showprogressbar:
                pbar.update(i+1)

        if self.showprogressbar:
            pbar.finish()

        if self.saveportfolio:
            self.save()

        trades = self.portfolio.trades
        profit = np.sum(trades["pl"])
        return profit, self.portfolio.ntrades
