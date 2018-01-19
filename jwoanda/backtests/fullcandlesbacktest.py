import logging
import signal

import numpy as np
from progressbar import Bar, ETA, Percentage, ProgressBar

from jwoanda.backtests.backtest import Backtest
from jwoanda.strategy import Strategy
from jwoanda.enums import Granularity, Events, VolumeGranularity
from jwoanda.oandaaccount import oandaenv
from jwoanda.history import HistoryManager
from jwoanda.candlemaker import CandleMakerThread
from jwoanda.strategytrading import StrategyTrading

class FullCandlesBacktest(Backtest):
    def __init__(self, strategy, **kwargs):
        super(FullCandlesBacktest, self).__init__(strategy, **kwargs)
        logging.info("init FullCandlesBacktest for strategy %s", strategy.name)
        
        granularity = kwargs.get("granularity", Granularity.S5)
        year = kwargs.get("year", 2016)
        self.candles = HistoryManager.getcandles(strategy.instrument, granularity, year)

        candlesperc = kwargs.get("candlesperc", -1)

        if candlesperc > 0. and candlesperc < 1.:
            self.candles.head(int(candlesperc * self.candles.ncandles), inplace=True)

        if not isinstance(self.strategy, Strategy):
            raise Exception("Not a strategy")


        self.doterminate = False
        #signal.signal(signal.SIGTERM, self.signal_term_handler)
        #signal.signal(signal.SIGINT, self.signal_term_handler)

        
    @property
    def instrument(self):
        return self.strategy.instrument      

    # def signal_term_handler(self, signal, frame):
    #     logging.info("Caught SIGINT/SIGTERM, exiting")
    #     self.doterminate = True

    def start(self):
        candles = self.candles.data
        if self.showprogressbar:
            pbar = ProgressBar(widgets=['Backtesting: ',
                                        Percentage(),
                                        Bar(),
                                        ETA()],
                               max_value=len(candles)).start()
        volmode = False
        if isinstance(self.strategy.granularity, VolumeGranularity):
            volmode = True

        if not volmode:
            time0 = candles[0]['time']
            time1 = time0 + self.strategy.granularity.value
        
        cmt = CandleMakerThread(self.strategy,
                                None,
                                resumefromhistory=False)
            
        for cnt, candle in enumerate(candles):

            if self.doterminate:
                break
            if not volmode:
                if candle['time'] >= time1:
                    cmt.makeCandle()
                    time1 = candle['time'] + self.strategy.granularity.value

            self.randomtickgenerator(candle, self.strategy.instrument, cmt)
            #self.simpletickgenerator(candles[i], instrument)


            if self.showprogressbar and (cnt % 1000 == 0):
                pbar.update(cnt+1)

        if self.showprogressbar:
            pbar.finish()

        if self.saveportfolio:
            self.save()

        trades = self.portfolio.trades
        pl = np.sum(trades["pl"])

        return pl, self.portfolio.ntrades
