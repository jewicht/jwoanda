from __future__ import print_function

import logging
try:
    from backports import lzma
except:
    import lzma
import pickle
import os

import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime
from scipy.stats import linregress, kde

from jwoanda.portfolio.analysisfcn import drawdown
from jwoanda.enums import ExitReason, PositionStatus
from jwoanda.instenum import Instruments
from jwoanda.portfolio.btportfolio import BTPortfolio
from jwoanda.utils import get_items

class Analysis(object):

    def __init__(self, backtest=None, portfolio=None):

        self.portfolio = None
        self.filename = None

        if backtest is not None:
            with lzma.open(backtest, mode='rb') as f:
                d = pickle.load(f)
                self.options = d['options']
                self.portfolio = d['portfolio']
                self.filename = backtest

        if portfolio is not None:
            self.portfolio = BTPortfolio()
            self.portfolio.load(portfolio)
            self.filename = portfolio
            self.options = None

        if self.portfolio is not None:
            self.filename, file_extension = os.path.splitext(self.filename)


            logging.basicConfig(level=logging.INFO,
                                format='%(message)s',
                                filename=self.filename + '.txt',
                                filemode='w')

            # define a Handler which writes INFO messages or higher to the sys.stderr
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            # set a format which is simpler for console use
            #formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            # tell the handler to use this format
            #console.setFormatter(formatter)
            # add the handler to the root logger
            logging.getLogger('').addHandler(console)

            if self.options is not None:
                logging.info("Parameters were")
                for key, val in get_items(self.options):
                    logging.info("{} = {}".format(key, val))
                logging.info("")
            
            self.analysis()


    def _histoplot(self, ax, trades):
        hlist = []
        for reason in [ExitReason.NORMAL, ExitReason.TS, ExitReason.TP, ExitReason.SL]:
            blu = trades[trades["closereason"] == reason.value]
            if len(blu) > 0:
                n, bins, patches = ax.hist(blu["plpips"], bins=50, label=reason.name)
                hlist.append(patches[0])
        ax.legend(handles=hlist)        

    def fitandplot(self, ax, x, y):
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        ax.plot(x, intercept + slope*x, 'r')
        ax.plot(x, 0.*x, 'C0')
        
        
    def subplot(self, ax, trades, col, title, axeslabels=False, fontsize=12):
        self._histoplot(ax[0, col], trades)
        ax[0, col].set_title(title)#, fontsize=fontsize)
        ax[1, col].plot(self.portfolio.initialbalance + np.cumsum(trades['pl']))

        
        x = (trades['closetime']-trades['opentime'])/3600.
        logging.info("longest trade = %f hours", np.max(x))
        y = trades['pl']

        self.fitandplot(ax[2, col], x, y)
        
        nbins=50
        try:
            k = kde.gaussian_kde([x,y])
            xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
            zi = k(np.vstack([xi.flatten(), yi.flatten()]))
            ax[2, col].pcolormesh(xi, yi, zi.reshape(xi.shape))
        except:
            pass

        x = np.array([datetime.fromtimestamp(x).hour + datetime.fromtimestamp(x).minute * 100. / 60. for x in trades['opentime']])
        self.fitandplot(ax[3, col], x, y)
        try:
            k = kde.gaussian_kde([x,y])
            xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
            zi = k(np.vstack([xi.flatten(), yi.flatten()]))
            ax[3, col].pcolormesh(xi, yi, zi.reshape(xi.shape))
        except:
            pass

        if axeslabels:
            ax[0, col].set_xlabel("P/L")#, fontsize=fontsize)
            ax[1, col].set_xlabel('time')#, fontsize=fontsize)
            ax[1, col].set_ylabel('P/L')#, fontsize=fontsize)
            ax[2, col].set_xlabel('trade duration [h]')#, fontsize=fontsize)
            ax[2, col].set_xlabel('P/L')#, fontsize=fontsize)
            ax[3, col].set_xlabel('trade open time [h]')#, fontsize=fontsize)
            ax[3, col].set_ylabel('P/L')#, fontsize=fontsize)

        
    def plot(self, alltrades, longtrades, shorttrades):
        fig, ax = plt.subplots(nrows=4, ncols=3, figsize=(40, 30))
        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        
        self.subplot(ax, alltrades, 0, 'All trades', axeslabels=True)
        self.subplot(ax, longtrades, 1, 'Long trades')
        self.subplot(ax, shorttrades, 2, 'Short trades')

        plt.show()
        if self.filename is not None:
            plt.savefig(self.filename + ".png")


    def showminmax(self, trades):
        logging.info("min/mean/max pl in pips = %.1f/%.1f/%.1f",
                     np.min(trades["plpips"]),
                     np.mean(trades["plpips"]),
                     np.max(trades["plpips"]))

        pt = trades[trades["plpips"] > 0.]
        if pt.size > 0:
            logging.info("Percentage of profitable trades     = %.1f%%, min/mean/max profit in pips = %.1f/%.1f/%.1f",
                         100.*pt.size/trades.size,
                         np.min(pt["plpips"]),
                         np.mean(pt["plpips"]),
                         np.max(pt["plpips"]))

            npt = trades[trades["plpips"] < 0.]
            if npt.size > 0:
                logging.info("Percentage of not-profitable trades = %.1f%%, min/mean/max loss in pips  = %.1f/%.1f/%.1f",
                             100.*npt.size/trades.size,
                             -1.*np.max(npt["plpips"]),
                             -1.*np.mean(npt["plpips"]),
                             -1.*np.min(npt["plpips"]))


    def analyze(self, alltrades):

        maxsuccloss, maxsuccwin, maxdrawdown = drawdown(alltrades["plpips"])
        logging.info("Max successive win   = %d", maxsuccwin)
        logging.info("Max successive loss  = %d", maxsuccloss)
        logging.info("Max drawdown in pips = %.1f", maxdrawdown)
        logging.info("")

        self.showminmax(alltrades)
        logging.info("Exit reason: normal = %.1f%%, TP = %1.f%%, SL = %.1f%%, TS = %.1f%%",
                     100.*alltrades[alltrades["closereason"] == ExitReason.NORMAL.value].size/alltrades.size,
                     100.*alltrades[alltrades["closereason"] == ExitReason.TP.value].size/alltrades.size,
                     100.*alltrades[alltrades["closereason"] == ExitReason.SL.value].size/alltrades.size,
                     100.*alltrades[alltrades["closereason"] == ExitReason.TS.value].size/alltrades.size)

        normaltrades = alltrades[alltrades["closereason"] == ExitReason.NORMAL.value]
        TPtrades = alltrades[alltrades["closereason"] == ExitReason.TP.value]
        TStrades = alltrades[alltrades["closereason"] == ExitReason.TS.value]
        SLtrades = alltrades[alltrades["closereason"] == ExitReason.SL.value]
        logging.info("")
        if normaltrades.size > 0:
            logging.info("For trades not stopped by TP/SL/TS")
            self.showminmax(normaltrades)
        if TPtrades.size > 0:
            logging.info("")
            logging.info("For trades stopped by TP")
            self.showminmax(TPtrades)
        if SLtrades.size > 0:
            logging.info("")
            logging.info("For trades stopped by SL")
            self.showminmax(SLtrades)
        if TStrades.size > 0:
            logging.info("")
            logging.info("For trades stopped by TS")
            self.showminmax(TStrades)


    def analysis(self):
        logging.info("Initial balance = %f", self.portfolio.initialbalance)
        logging.info("Final balance   = %f", self.portfolio.account.balance)
        logging.info("")

        alltrades = self.portfolio.trades#.trades 
        alltrades = alltrades[alltrades["status"] == PositionStatus.CLOSED]

        if False:
            from prettytable import PrettyTable
            dat = alltrades[:10]
            x = PrettyTable(dat.dtype.names)
            for row in dat:
                x.add_row(row)
            logging.info(x.get_string(border=False))


        tradedinstruments = list(set(alltrades["instrument"]))
        strategies = list(set(alltrades["strategy"]))

        for strategy in strategies:

            logging.info("Strategy = %s", strategy)
            trades = alltrades[alltrades["strategy"] == strategy]

            #logging.info(trades["opentime"])
            longtrades = trades[trades["units"] > 0.]
            shorttrades = trades[trades["units"] < 0.]

            logging.info("Number of trades = %d (%.1f%% long, %.1f%% short)",
                         trades.size,
                         100.*longtrades.size/trades.size,
                         100.*shorttrades.size/trades.size)
            logging.info("")

            if longtrades.size > 0:
                logging.info("Long analysis")
                logging.info("=============")
                logging.info("")
                self.analyze(longtrades)
                logging.info("")

            if shorttrades.size > 0:
                logging.info("Short analysis")
                logging.info("==============")
                logging.info("")
                self.analyze(shorttrades)

            self.plot(trades, longtrades, shorttrades)

