from __future__ import print_function

import logging
import threading
import time
import sys
from datetime import datetime

import v20

from jwoanda.portfolio.portfolio import Portfolio
from jwoanda.instenum import Instruments
from jwoanda.history import floattostr
from jwoanda.oandaaccount import oandaenv

class OandaPortfolioManager(threading.Thread):
    def __init__(self, oandaportfolio, trigger, pipelist):
        super(OandaPortfolioManager, self).__init__()
        self.portfolio = oandaportfolio
        self.trigger = trigger
        self.pipelist = pipelist
        self.kill = False


    def run(self):
        while not self.kill:
            self.trigger.get()
            for pipe in self.pipelist:
                try:
                    data = pipe.recv(block=False)
                    action = data['action']
                    args = data['args']

                    if action == 'open':
                        ret = self.portfolio.open(args['strategy'], args['instrument'], args['units'])
                        pipe.send(ret)
                    elif action == 'close':
                        ret = self.portfolio.close(args['tradeID'], args['reason'])
                        pipe.send(ret)
                    else:
                        pass
                except:
                    pass


    def disconnect(self):
        self.kill = True



class OandaPortfolioProxy(Portfolio):
    def __init__(self, trigger, pipe):
        super(OandaPortfolioProxy, self).__init__()
        self.trigger = trigger
        self.pipe = pipe


    def openposition(self, strategy, instrument, units, **kwargs):
        args = {}
        args['action'] = 'open'
        args['args'] = {'strategy': strategy, 'instrument': instrument, 'units': units}
        self.pipe.send(args)
        self.trigger.put(0)
        return self.pipe.recv()


    def closeposition(self, tradeID, reason):
        args = {}
        args['action'] = 'close'
        args['args'] = {'tradeID':tradeID, 'reason': reason}
        self.pipe.send(args)
        self.trigger.put(0)
        return self.pipe.recv()


    def picklename(self):
        return "none"



class OandaPortfolio(Portfolio):
    def __init__(self):
        super(OandaPortfolio, self).__init__()

        uselocking = False
        self._lock = threading.Lock() if uselocking else None

        self._api = oandaenv.api()
        res = self._api.account.summary(oandaenv.account_id)
        self.account = res.get('account')
        #account.currency
        #account.balance
        #account.NAV
        #account.marginRate
        #account.marginUsed
        #account.marginAvailable


        res = self._api.position.list_open(oandaenv.account_id)
        positions = res.get('positions')
        for position in positions:
            # instrument: EUR_USD
            # pl: 0.002
            # unrealizedPL: -0.0002
            # resettablePL: 0.002
            # long:
            #   units: 0.0
            #   pl: 0.0012
            #   unrealizedPL: 0.0
            #   resettablePL: 0.0012
            # short:
            #   units: -1.0
            #   averagePrice: 1.06083
            #   tradeIDs:
            #   - '240'
            #   pl: 0.0008
            #   unrealizedPL: -0.0002
            #   resettablePL: 0.0008

            instrument = Instruments[position.instrument]
            if position.long.units != 0:
                self.setposition(instrument, position.long.units)
            if position.short.units != 0:
                self.setposition(instrument, position.short.units)

        res = self._api.trade.list_open(oandaenv.account_id)
        trades = res.get('trades')
        for trade in trades:
            # id: '240'
            # instrument: EUR_USD
            # price: 1.06083
            # openTime: '1487943553.938119500'
            # state: OPEN
            # initialUnits: -1.0
            # currentUnits: -1.0
            # realizedPL: 0.0
            # unrealizedPL: -0.0001
            # financing: 0.0
            oandaID = int(trade.id)
            price = float(trade.price)
            units = int(trade.currentUnits)
            self.addTrade(instrument=Instruments[trade.instrument],
                          oandaID=oandaID,
                          units=units,
                          opentime=float(trade.openTime),
                          openaskedprice=price,
                          openreceivedprice=price)
            logging.info("Adding existing trade oandaID=%d, instrument=%s, units=%f",
                         oandaID,
                         trade.instrument,
                         units)


    def lock(self):
        if self._lock is not None:
            self._lock.acquire()


    def unlock(self):
        if self._lock is not None:
            self._lock.release()


    def apiordermarket(self, instrument, units, **arguments):
        ntries = 0
        while ntries < 5:
            try:
                response = self._api.order.market(oandaenv.account_id,
                                                  instrument=instrument.name,
                                                  units=units,
                                                  **arguments)
                return response
            except v20.errors.V20Timeout:
                ntries += 1
                time.sleep(0.5)
            except v20.errors.V20ConnectionError:
                ntries += 1
                time.sleep(0.5)
        return None


    def openposition(self, strategy, instrument, units, **kwargs):
        self.lock()

        if self.currentposition(instrument) != 0:
            logging.warning("A position is already opened")

        _time, bid, ask = self.price(instrument)

        stoploss = kwargs.get("stoploss", -1.)
        takeprofit = kwargs.get("takeprofit", -1.)
        trailingstop = kwargs.get("trailingstop", -1.)
        spread = ask - bid

        price = ask if units > 0. else bid

        arguments = {}
        if stoploss > 0.:
            arguments['stopLossOnFill'] = v20.transaction.StopLossDetails(price=stoploss)
        if takeprofit > 0.:
            arguments['takeProfitOnFill'] = v20.transaction.TakeProfitDetails(price=takeprofit)
        if trailingstop > 0.:
            arguments['trailingStopLossOnFill'] = v20.transaction.TrailingStopLossDetails(distance=trailingstop)

        response = self.apiordermarket(instrument, units, **arguments)

        if response is None:
            logging.error('Couln\'t send the order. Network problem?')
            return -1

        if response.status == 400:
            logging.error('Couldn\'t open the order: 400 The Order specification was invalid')
            try:
                logging.error(response.get('errorMessage'))
            except:
                pass
            return -1
        elif response.status == 404:
            logging.error('Couldn\'t open the order: 404 The Order or Account specified does not exist.')
            try:
                logging.error(response.get('errorMessage'))
            except:
                pass
            return -1
        elif response.status != 201:
            logging.error('Unknown error message: status = {}'.format(response.status))
            try:
                logging.error(response.get('errorMessage'))
            except:
                pass
            return -1

        orderCT = response.get('orderCreateTransaction')
        #id: '245'
        #time: '1487945572.767654923'
        #userID: 5383513
        #accountID: 101-004-5383513-001
        #batchID: '245'
        #type: MARKET_ORDER
        #instrument: EUR_USD
        #units: 1.0
        #timeInForce: FOK
        #positionFill: DEFAULT
        #reason: CLIENT_ORDER

        if hasattr(response, 'orderFillTransaction') is None:
            logging.error('Order was not filled. orderFillTransaction is None')
            return -1

        orderFT = response.get('orderFillTransaction')
        # id: '246'
        # time: '1487945572.767654923'
        # userID: 5383513
        # accountID: 101-004-5383513-001
        # batchID: '245'
        # type: ORDER_FILL
        # orderID: '245'
        # instrument: EUR_USD
        # units: 1.0
        # price: 1.0598
        # reason: MARKET_ORDER
        # pl: 0.0
        # financing: 0.0
        # accountBalance: 99999.9946
        # tradeOpened:
        #   tradeID: '246'
        #   units: 1.0


        pricereceived = float(orderFT.price)
        timereceived = float(orderFT.time)

        if orderFT.tradesClosed is not None:
            for tradeClosed in orderFT.tradesClosed:
                oandaID = int(tradeClosed.tradeID)
                realizedPL = float(tradeClosed.realizedPL)
                self.closeTrade(oandaID=oandaID, profit=realizedPL)


        if orderFT.tradeReduced is not None:
            #  tradeReduced:
            #  tradeID: '312'
            #  units: -1.0
            #  realizedPL: -0.0001
            #  financing: 0.0
            oandaID = int(orderFT.tradeReduced.tradeID)
            realizedPL = float(orderFT.tradeReduced.realizedPL)
            self.closeTrade(oandaID=oandaID, profit=realizedPL)


        if orderFT.tradeOpened is not None:
            #print(orderFT.tradeOpened)
            oandaID = int(orderFT.tradeOpened.tradeID)
            _time = float(orderFT.time)
            logging.info("Open trade #%d: %f units of %s @ %s",
                         oandaID,
                         units,
                         instrument.name,
                         floattostr(pricereceived, instrument.displayPrecision))

            tradeID = self.addTrade(stategy=strategy,
                                    instrument=instrument,
                                    status=0,
                                    units=units,
                                    openaskedprice=price,
                                    openreceivedprice=pricereceived,
                                    oandaID=oandaID,
                                    openspread=spread,
                                    opentime=_time,
                                    stoploss=stoploss,
                                    takeprofit=takeprofit,
                                    trailingstop=trailingstop)

            self.unlock()
            return tradeID

        else:
            self.unlock()
            return -1


    def apitradeclose(self, oandaID):
        ntries = 0
        while ntries < 5:
            try:
                response = self._api.trade.close(oandaenv.account_id, oandaID)
                return response
            except v20.errors.V20Timeout:
                ntries += 1
                time.sleep(0.5)
            except v20.errors.V20ConnectionError:
                ntries += 1
                time.sleep(0.5)
        return None


    def closeposition(self, tradeID, reason):
        if tradeID < 0 or tradeID is None:
            logging.error("invalid tradeID")
            return

        trade = self.trades[tradeID]
        oandaID = trade['oandaID']
        units = trade['units']
        instrument = Instruments[trade["instrument"]]
        _time, bid, ask = self.price(instrument)

        self.lock()


        spread = ask - bid
        price = bid if units > 0. else ask

        logging.info("Trying to close #%d: %f units of %s",
                     oandaID,
                     units,
                     instrument.name)
        response = self.apitradeclose(oandaID)

        if response is None:
            logging.error('Couldn\'t close the trade. Network problem?')
            self.unlock()
            return

        if response.status == 400:
            logging.error('Couldn\'t open the order: 400 The Order specification was invalid')
            try:
                logging.error(response.get('errorMessage'))
            except:
                pass
            self.unlock()
            return
        elif response.status == 404:
            logging.error('Couldn\'t open the order: 404 The Order or Account specified does not exist.')
            try:
                logging.error(response.get('errorMessage'))
            except:
                pass
            return
        elif response.status != 201 and response.status != 200:
            logging.error('Unknown error message: status = {}'.format(response.status))
            try:
                logging.error(response.get('errorMessage'))
            except:
                pass
            self.unlock()
            return

        orderCT = response.get('orderCreateTransaction')
        # id: '241'
        # time: '1487944704.360123894'
        # userID: 5383513
        # accountID: 101-004-5383513-001
        # batchID: '241'
        # type: MARKET_ORDER
        # instrument: EUR_USD
        # units: 1.0
        # timeInForce: FOK
        # positionFill: REDUCE_ONLY
        # tradeClose:
        #   tradeID: '240'
        #   units: ALL
        # reason: TRADE_CLOSE

        orderFT = response.get('orderFillTransaction')
        # id: '242'
        # time: '1487944704.360123894'
        # userID: 5383513
        # accountID: 101-004-5383513-001
        # batchID: '241'
        # type: ORDER_FILL
        # orderID: '241'
        # instrument: EUR_USD
        # units: 1.0
        # price: 1.06117
        # reason: MARKET_ORDER_TRADE_CLOSE
        # pl: -0.0003
        # financing: 0.0
        # accountBalance: 99999.9946
        # tradesClosed:
        # - tradeID: '240'
        #   units: 1.0
        #   realizedPL: -0.0003
        #   financing: 0.0

        profit = orderFT.pl
        pricereceived = orderFT.price
        _time = orderFT.time

        logging.info("Closed trade #%d: %f units of %s @ %s",
                     oandaID,
                     units,
                     instrument.name,
                     floattostr(pricereceived, instrument.displayPrecision))

        self.closeTrade(tradeID=tradeID, reason=reason, closeaskedprice=price, closereceivedprice=pricereceived, spread=spread, time=_time)
        self.unlock()


    # def closepositionTLSL(self, oandaID, reason, price, spread, time):
    #     #self.lock.acquire()
    #     self.closeorder(oandaID=oandaID, reason=reason, closeaskedprice=price, closereceivedprice=price, spread=spread, time=time)
    #     #self.lock.release()

    def picklename(self):
        pythonver = "py%d%d" % (sys.version_info.major, sys.version_info.minor)
        enddate = datetime.now()
        return "oanda-%s-%s-%s-%s.portfolio" % (oandaenv.account_id, self._startdate.strftime("%Y%m%d%H%M"), enddate.strftime("%Y%m%d%H%M"), pythonver)
