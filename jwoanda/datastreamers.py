from __future__ import print_function

import logging
import threading
import time
import numpy as np

import v20

from jwoanda.instenum import Instruments
from jwoanda.history import floattostr
from jwoanda.oandaaccount import oandaenv
from jwoanda.utils import get_items
from jwoanda.enums import Events

class HeartbeatCheck(threading.Thread):
    def __init__(self, obj, method, name, delay=5):
        super(HeartbeatCheck, self).__init__(name=name)
        self.kill = False
        self.obj = obj
        self.method = method
        self.delay = delay

    def run(self):
        while self.kill != True:
            time.sleep(1)
            if getattr(self.obj, self.method) is None:
                continue
            timediff = time.time() - getattr(self.obj, self.method)
            if timediff > self.delay:
                logging.error("Did not receive any data since %s seconds",
                              floattostr(timediff, 1))

    def disconnect(self):
        self.kill = True


        
class TransactionsStreamer(threading.Thread):
    def __init__(self, portfolio):
        super(TransactionsStreamer, self).__init__(name="TransactionsStreamer")
        self.portfolio = portfolio
        self.lastheartbeattime = None
        self.kill = False


    def run(self):
        while not self.kill:
            try:
                response = oandaenv.streamingapi().transaction.stream(oandaenv.account_id)
                for msg_type, msg in response.parts():
                    if self.kill:
                        return
                    self.process(msg_type, msg)
            except v20.errors.V20ConnectionError:
                time.sleep(0.5)
            except v20.errors.V20Timeout:
                time.sleep(0.5)


    def process(self, msg_type, msg):
        if msg_type == "transaction.TransactionHeartbeat":
            self.lastheartbeattime = time.time()
        elif msg_type == 'transaction.Transaction':
            if msg.type == 'MARKET_ORDER':
                # {"accountID":"101-002-1179508-001",
                #  "batchID":"777",
                #  "id":"777",
                #  "instrument":"EUR_USD",
                #  "positionFill":"DEFAULT","
                #  reason":"CLIENT_ORDER",
                #  "time":"2016-09-20T18:18:22.126490230Z",
                #  "timeInForce":"FOK",
                #  "type":"MARKET_ORDER",
                #  "units":"100",
                #  "userID":1179508}
                pass
            elif msg.type == 'ORDER_FILL':
                # {"accountBalance":"6505973.49885",
                #  "accountID":"<ACCOUNT>",
                #  "batchID":"777",
                #  "financing":"0.00000",
                #  "id":"778",
                #  "instrument":"EUR_USD",
                #  "orderID":"777",
                #  "pl":"0.00000",
                #  "price":"1.11625",
                #  "reason":"MARKET_ORDER",
                #  "time":"2016-09-20T18:18:22.126490230Z",
                #  "tradeOpened":{"tradeID":"778","units":"100"},
                #  "type":"ORDER_FILL",
                #  "units":"100",
                #  "userID":1179508}
                pass
            elif msg.type == 'TAKE_PROFIT_ORDER':
                logging.info(msg.type)
                logging.info(msg)
            elif msg.type == 'STOP_LOSS_ORDER':
                logging.info(msg.type)
                logging.info(msg)
            elif msg.type == 'ORDER_CANCEL':
                logging.info(msg.type)
                logging.info(msg)
            else:
                logging.info(msg.type)
                logging.info(msg)
        else:
            logging.info('No action for this msg: %s', msg_type)

    def disconnect(self):
        logging.debug("Disconnecting")
        self.kill = True


    
class RatesStreamer(threading.Thread):
    def __init__(self, tickQueues, instruments, portfolio, gtkinterface, **kwargs):
        super(RatesStreamer, self).__init__(name="RatesStreamer")
        self.instruments = set(instruments)

        self.lastheartbeattime = None
        self.lastpricetime = None
        
        self.tickQueues = tickQueues
        self.portfolio = portfolio
        self.kill = False
        self.gtkinterface = gtkinterface
        self.restart = False
        self.docheckTPSL = kwargs.get("docheckTPSL", False)


    def addInstrument(self, instrument):
        self.instruments.add(instrument)
        self.restart = True

    def setTickQueues(self, tickqueues):
        self.tickQueues = tickqueues

    def run(self):
        logging.info("Running: instruments = %s", ','.join([i.name for i in self.instruments]))
        while not self.kill:
            self.restart = False
            self.realrun()


    def realrun(self):
        while not self.kill:
            try:
                response = oandaenv.streamingapi().pricing.stream(
                    oandaenv.account_id,
                    instruments=','.join([i.name for i in self.instruments])
                )
    
                for msg_type, msg in response.parts():
                    if self.kill or self.restart:
                        return
                    self.process(msg_type, msg)
            except v20.errors.V20ConnectionError:
                time.sleep(0.5)
            except v20.errors.V20Timeout:
                time.sleep(0.5)


    def process(self, msg_type, msg):
        if msg_type == "pricing.PricingHeartbeat":
            self.lastheartbeattime = time.time()
        elif msg_type == "pricing.Price":

            # type: PRICE
            # instrument: EUR_GBP
            # time: '1487973598.721325319'
            # status: non-tradeable
            # bids:
            # - price: 0.84687
            #   liquidity: 1000000.0
            # - price: 0.84686
            #   liquidity: 2000000.0
            # - price: 0.84685
            #   liquidity: 5000000.0
            # - price: 0.84683
            #   liquidity: 10000000.0
            # asks:
            # - price: 0.84795
            #   liquidity: 1000000.0
            # - price: 0.84796
            #   liquidity: 2000000.0
            # - price: 0.84797
            #   liquidity: 5000000.0
            # - price: 0.84799
            #   liquidity: 10000000.0
            # closeoutBid: 0.84683
            # closeoutAsk: 0.84799
            
            instrument = Instruments[msg.instrument]
            _time = np.float64(msg.time)
            #bid = np.float64(msg.closeoutBid)
            #ask = np.float64(msg.closeoutAsk)
            bid = np.float64(msg.bids[0].price)
            ask = np.float64(msg.asks[0].price)
            self.lastpricetime = time.time()

            #update price in portfolio
            marketopen = not (msg.status == 'non-tradeable')
            self.portfolio.setprice(instrument, (_time, bid, ask, marketopen))    
            
            if self.gtkinterface:
                self.gtkinterface.setprice(msg.instrument, bid, ask)
                    
            #send the tick to the Candle
            tick = (instrument, _time, bid, ask)

            if self.docheckTPSL:
                self.portfolio.checkTPSL(tick)

            logging.debug("%s bid=%f ask=%f", instrument.name, bid, ask)
            for eq in self.tickQueues:
                if instrument in eq['instruments']:
                    eq['queue'].put({'type': Events.TICK, 'tick': tick})

        else:
            pass


    def disconnect(self):
        logging.debug("Disconnecting")
        self.kill = True



class FakeRatesStreamer(threading.Thread):
    def __init__(self, tickQueues, instruments, portfolio, **kwargs):
        super(FakeRatesStreamer, self).__init__(name=FakeRatesStreamer)
        self.instruments = instruments

        self.lastheartbeattime = None
        self.lastpricetime = None
        
        self.tickQueues = tickQueues
        self.portfolio = portfolio

        self.kill = False

        self.prices = {}
        for instrument in self.instruments:
            self.prices[instrument] = np.random.random()

    def addInstrument(self, instrument):
        self.instruments.add(instrument)
        self.restart = True

    def setTickQueues(self, tickqueues):
        self.tickQueues = tickqueues

    def run(self):
        #logging.info("Running: instruments = %s", ','.join(self.instruments))

        while not self.kill:

            for instrument in self.instruments:

                self.lastpricetime = self.lastheartbeattime = time.time()

                self.prices[instrument] += (np.random.random_integers(10) - 5) * instrument.pip * 0.1
                
                _time = np.float64(self.lastpricetime)
                bid = self.prices[instrument]
                ask = self.prices[instrument] + instrument.pip

                #update price in portfolios
                self.portfolio.setprice(instrument, (_time, bid, ask, True))

                tick = (instrument, _time, bid, ask)
                #send the tick to the CandleMaker
                for tq in self.tickQueues:
                    if instrument in tq['instruments']:
                        tq['queue'].put(tick)
            time.sleep(0.25)


    def disconnect(self):
        logging.debug("Disconnecting")
        self.kill = True
