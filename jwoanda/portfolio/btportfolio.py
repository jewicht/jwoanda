import logging
import sys

from jwoanda.portfolio.portfolio import Portfolio
from jwoanda.instenum import Instruments

class BTPortfolio(Portfolio):
    def __init__(self, balance=100000., currency='GBP'):
        #self.tradecnt = 0
        super(BTPortfolio, self).__init__()

        if balance < 0.:
            raise Exception("Invalid balance %s" % balance)
        self.initialbalance = balance
        self.account.balance = self.initialbalance
        self.account.NAV = self.initialbalance

        if currency not in ['EUR', 'GBP', 'CHF', 'JPY', 'USD']:
            raise Exception("Invalid currency %s" % currency)
        self.account.currency = currency


    def openposition(self, strategy, instrument, units, **kwargs):
        time, bid, ask = self.price(instrument)

        spread = ask - bid
        stoploss = kwargs.get("stoploss", 0.)
        takeprofit = kwargs.get("takeprofit", 0.)
        trailingstop = kwargs.get("trailingstop", 0.)
        lifetime = kwargs.get("lifetime", 0.)
        tsextrema = 0.

        price = ask if units > 0 else bid

        if trailingstop > 0.:
            tsextrema = bid if units > 0 else ask

        if self.currentposition(instrument) != 0:
            logging.warning("A position is already opened")

        tradeID = self.addTrade(strategy=strategy,
                                instrument=instrument,
                                status=0,
                                units=units,
                                openaskedprice=price,
                                openreceivedprice=price,
                                openspread=spread,
                                opentime=time,
                                stoploss=stoploss,
                                takeprofit=takeprofit,
                                trailingstop=trailingstop,
                                lifetime=lifetime,
                                tsextrema=tsextrema)

        return tradeID


    def closeposition(self, tradeID, reason):
        units = self.trades[tradeID]['units']
        instrument = Instruments[self.trades[tradeID]['instrument']]
        time, bid, ask = self.price(instrument)

        spread = ask - bid
        price = bid if units > 0 else ask
        self.closeTrade(tradeID=tradeID, reason=reason, closeaskedprice=price, closereceivedprice=price, spread=spread, time=time)


    def picklename(self):
        pythonver = "py%d%d" % (sys.version_info.major, sys.version_info.minor)
        return "BT-%s-%s.portfolio" % (self._startdate.strftime("%Y%m%d%H%M"), pythonver)
