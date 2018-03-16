from __future__ import print_function
from abc import ABCMeta, abstractmethod
import logging
import threading
try:
    from backports import lzma
except:
    import lzma
try:
    import cPickle as pickle
except:
    import pickle
import copy
import os
import sys
from datetime import datetime
from six import with_metaclass
import pathlib2

import numpy as np
import v20

from jwoanda.enums import PositionStatus, ExitReason
from jwoanda.instenum import Instruments
from jwoanda.oandaaccount import oandaenv
from jwoanda.utils import get_items

class Portfolio(with_metaclass(ABCMeta)):

    def __init__(self):

        self._openedtrades = []
        self._trades = self.zerodata(10000)
        self._ntrades = 0

        self._account = v20.account.AccountSummary()
        self._prices = np.zeros(len(Instruments),
                                [('time', np.float64),
                                 ('bid', np.float64),
                                 ('ask', np.float64),
                                 ('tradeable', np.bool)
                                ])
        self._positions = np.zeros(len(Instruments), [('units', np.int32)])
        self._startdate = datetime.now()


    @property
    def openedtrades(self):
        return self._openedtrades


    @property
    def account(self):
        return self._account


    @account.setter
    def account(self, value):
        self._account = value


    @property
    def trades(self):
        return self._trades


    @trades.setter
    def trades(self, value):
        self._trades = value


    @property
    def ntrades(self):
        return self._ntrades


    @ntrades.setter
    def ntrades(self, value):
        self._ntrades = value


    def settradeable(self, instrument, b):
        self._prices[instrument.ID]['tradeable'] = b


    def istradeable(self, instrument):
        return self._prices[instrument.ID]['tradeable']


    def zerodata(self, size):
        return np.zeros(size, dtype=[('status', np.uint8),
                                     ('instrument', 'U10'),
                                     ('closereason', np.uint8),
                                     ('strategy', 'U30'),
                                     ('units', np.int64),
                                     ('closespread', np.float64),
                                     ('openspread', np.float64),
                                     ('openaskedprice', np.float64),
                                     ('openreceivedprice', np.float64),
                                     ('closeaskedprice', np.float64),
                                     ('closereceivedprice', np.float64),
                                     ('opentime', np.float64),
                                     ('closetime', np.float64),
                                     ('pl', np.float64),
                                     ('plpips', np.float64),
                                     ('stoploss', np.float64),
                                     ('takeprofit', np.float64),
                                     ('trailingstop', np.float64),
                                     ('lifetime', np.float64),
                                     ('tsextrema', np.float64),
                                     ('oandaID', np.uint64)])


    def addTrade(self, **kwargs):
        tradeID = self.ntrades
        if tradeID >= self.trades.size:
            self.trades = np.append(self.trades, self.zerodata(self.trades.size))

        order = self.trades[tradeID]

        #required arguments
        instrument = kwargs.get('instrument')
        order["openaskedprice"] = kwargs.get('openaskedprice')
        order["openreceivedprice"] = kwargs.get('openreceivedprice')
        order["opentime"] = kwargs.get('opentime')
        order["units"] = units = kwargs.get('units')

        #optional arguments
        order["strategy"] = kwargs.get('strategy', 'noname')
        order["instrument"] = instrument.name
        order["status"] = PositionStatus.OPENED
        order["stoploss"] = kwargs.get('stoploss', 0.)
        order["takeprofit"] = kwargs.get('takeprofit', 0.)
        order["trailingstop"] = kwargs.get('trailingstop', 0.)
        order["lifetime"] = kwargs.get('lifetime', 0.)
        order["tsextrema"] = kwargs.get('tsextrema', 0.)
        order["oandaID"] = kwargs.get('oandaID', -1)

        #print("append ", id)
        self.openedtrades.append(tradeID)
        #print(self.openordersid)
        self.ntrades += 1

        self.changeposition(instrument, units)
        return tradeID


    def closeTrade(self, **kwargs):
        reason = kwargs.get("reason", ExitReason.NOREASON)

        oandaID = kwargs.get("oandaID", None)
        if oandaID is None:
            tradeID = kwargs.get("tradeID")
        else:
            for cnt in self.openedtrades:
                if self.trades[cnt]['oandaID'] == oandaID:
                    tradeID = cnt
                    break
            logging.error("Couldn't find order %d. Couldn't close it", oandaID)
            return

        closeaskedprice = kwargs.get("closeaskedprice", 0.)
        closereceivedprice = kwargs.get("closeaskedprice", 0.)
        spread = kwargs.get("spread", 0.)
        time = kwargs.get("time", 0.)

        order = self.trades[tradeID]
        if order["status"] == PositionStatus.OPENED:
            order["status"] = PositionStatus.CLOSED
            order["closereason"] = reason.value
            order["closeaskedprice"] = closeaskedprice
            order["closereceivedprice"] = closereceivedprice
            order["closespread"] = spread
            order["closetime"] = time

            instrument = Instruments[order["instrument"]]

            profit = kwargs.get("profit")
            if profit is None:
                profit = (closereceivedprice - order["openreceivedprice"]) * order["units"]

            order["pl"] = profit
            order['plpips'] = profit / abs(order['units']) / instrument.pip

            self.account.balance += profit
            self.changeposition(instrument, -order['units'])

            self.openedtrades.remove(tradeID)
        else:
            logging.debug("Position was already closed by TP/SL/TS")


    def load(self, filename):
        f = lzma.open(filename, mode='rb')
        tmp_dict = pickle.load(f)
        f.close()
        self.__dict__.update(tmp_dict)


    @abstractmethod
    def picklename(self):
        pass


    def save(self, filename=None, datadir=None):
        tmp_dict = copy.copy(self.__dict__)
        for key, val in get_items(tmp_dict):
            if isinstance(val, type(threading.Lock())):
                del tmp_dict[key]

        directory = datadir
        if datadir is None:
            datadir = oandaenv.datadir
            directory = os.path.expanduser(os.path.join(datadir, "portfolios"))

        pathlib2.Path(directory).mkdir(parents=True, exist_ok=True)    

        if filename is None:
            filename = self.picklename()

        filename = os.path.join(directory, filename)
        logging.info("Saving portfolio to %s", filename)
        f = lzma.open(filename, mode='wb')
        pickle.dump(tmp_dict, f)
        f.close()


    def changeposition(self, instrument, value):
        self._positions[instrument.ID]['units'] += value


    def setposition(self, instrument, value):
        self._positions[instrument.ID]['units'] = value


    def currentposition(self, instrument):
        return self._positions[instrument.ID]['units']


    def setprice(self, instrument, value):
        self._prices[instrument.ID] = value


    def setbid(self, instrument, value):
        self._prices[instrument.ID]['bid'] = value


    def setask(self, instrument, value):
        self._prices[instrument.ID]['ask'] = value


    def settime(self, instrument, value):
        self._prices[instrument.ID]['time'] = value


    def price(self, instrument):
        thisprice = self._prices[instrument.ID]
        return (thisprice['time'], thisprice['bid'], thisprice['ask'])


    def bid(self, instrument):
        return self._prices[instrument.ID]['bid']


    def ask(self, instrument):
        return self._prices[instrument.ID]['ask']


    def time(self, instrument):
        return self._prices[instrument.ID]['time']


    @abstractmethod
    def openposition(self):
        pass


    @abstractmethod
    def closeposition(self, tradeID, reason):
        pass


    def checkTPSL(self, tick):
        instrument, time, bid, ask = tick

        for tradeID in self.openedtrades:
            order = self.trades[tradeID]
            if order['instrument'] != instrument.name:
                continue

            #lifetime
            if order['lifetime'] > 0. and (time - order['opentime'] > order['lifetime']):            
                self.closeposition(tradeID, ExitReason.LIFETIME)
                continue

            #check StopLoss, TakeProfit, TrailingStop
            if order['units'] > 0: # long
                if order["stoploss"] > 0:
                    if bid < order["stoploss"]:
                        self.closeposition(tradeID, ExitReason.SL)
                        continue
                if order["takeprofit"] > 0:
                    if bid > order["takeprofit"]:
                        self.closeposition(tradeID, ExitReason.TP)
                        continue
                if order["trailingstop"] > 0:
                    if bid < order["tsextrema"] - order["trailingstop"] * instrument.pip:
                        self.closeposition(tradeID, ExitReason.TS)
                        continue
                    if bid > order["tsextrema"]:
                        order["tsextrema"] = bid

            else: # short
                if order["stoploss"] > 0:
                    if ask > order["stoploss"]:
                        self.closeposition(tradeID, ExitReason.SL)
                        continue
                if order["takeprofit"] > 0:
                    if ask < order["takeprofit"]:
                        self.closeposition(tradeID, ExitReason.TP)
                        continue
                if order["trailingstop"] > 0:
                    #logging.info("tsetrema = {}".format(order["tsextrema"]))
                    if ask > order["tsextrema"] + order["trailingstop"] * instrument.pip:
                        self.closeposition(tradeID, ExitReason.TS)
                        continue
                    if ask < order["tsextrema"]:
                        order["tsextrema"] = ask


    def closeallpositions(self, reason, instrument=None):
        for tradeID in self.openedtrades:
            if instrument is None:
                self.closeposition(tradeID, reason)
            elif instrument.name == self.trades[tradeID]['instrument']:
                self.closeposition(tradeID, reason)

    def isTradeOpen(self, tradeID):
        return tradeID in self.openedtrades
