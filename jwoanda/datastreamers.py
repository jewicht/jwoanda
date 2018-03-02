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
    def __init__(self, portfolio, **kwargs):
        super(TransactionsStreamer, self).__init__(**kwargs)
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
                # id, time, userID, accountID, batchID, instrument, units, timeInForce, positionFill, reason
                pass
            elif msg.type == 'ORDER_FILL':
                # id, time, userID, accountID, batchID, orderID, instrument, units, price, 
                pass
            elif msg.type == 'TAKE_PROFIT_ORDER':
                #print(msg.type)
                #print(msg)
                pass
            elif msg.type == 'STOP_LOSS_ORDER':
                #print(msg.type)
                #print(msg)
                pass
            elif msg.type == 'ORDER_CANCEL':
                #print(msg.type)
                #print(msg)
                pass
            else:
                print(msg)
        else:
            logging.info('No action for this msg: %s', msg_type)

    def disconnect(self):
        logging.debug("Disconnecting")
        self.kill = True


    
class RatesStreamer(threading.Thread):
    def __init__(self, tickQueues, instruments, portfolios, gtkinterface, **kwargs):
        super(RatesStreamer, self).__init__(**kwargs)
        self.instruments = set(instruments)

        self.lastheartbeattime = None
        self.lastpricetime = None
        
        self.tickQueues = tickQueues
        self.portfolios = portfolios
        self.kill = False
        self.gtkinterface = gtkinterface
        self.restart = False


    def addinstrument(self, instrument):
        self.instruments.add(instrument)
        self.restart = True


    def run(self):
        logging.info("Running: instruments = %s", ','.join(self.instruments))
        while not self.kill:
            self.realrun()


    def realrun(self):
        while not self.kill:
            try:
                response = oandaenv.streamingapi().pricing.stream(
                    oandaenv.account_id,
                    instruments=','.join(self.instruments)
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
                
            if msg.status == 'non-tradeable':
                logging.error("Market is closed")
                for portfolio in self.portfolios:
                    portfolio.marketclosed(instrument, True)

            self.lastpricetime = time.time()
            instrument = Instruments[msg.instrument]
            _time = np.float64(msg.time)
            #bid = np.float64(msg.closeoutBid)
            #ask = np.float64(msg.closeoutAsk)
            bid = np.float64(msg.bids[0].price)
            ask = np.float64(msg.asks[0].price)

            #update price in portfolios
            for portfolio in self.portfolios:
                portfolio.setprice(instrument, (_time, bid, ask, True))
                
            if self.gtkinterface:
                self.gtkinterface.setprice(msg.instrument, bid, ask)
                    
            #send the tick to the Candle
            tick = (instrument, _time, bid, ask)
            for eq in self.tickQueues:
                for i, g in eq['iglist']:
                    if i == instrument:
                        eq['queue'].put({'type': Events.TICK, 'tick': tick})

        else:
            pass

    def disconnect(self):
        logging.debug("Disconnecting")
        self.kill = True



class FakeRatesStreamer(threading.Thread):
    def __init__(self, tickQueues, instruments, portfolios, **kwargs):
        super(FakeRatesStreamer, self).__init__(**kwargs)
        self.instruments = [Instruments[instrument] for instrument in instruments]

        self.lastheartbeattime = None
        self.lastpricetime = None
        
        self.tickQueues = tickQueues
        self.portfolios = portfolios

        self.kill = False

        self.prices = {}
        for instrument in self.instruments:
            self.prices[instrument] = np.random.random()


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
                for portfolio in self.portfolios:
                    portfolio.setprice(instrument, (_time, bid, ask))

                tick = (instrument, _time, bid, ask)
                #send the tick to the CandleMaker
                for key, value in get_items(self.tickQueues):
                    if instrument in key:
                        value.put(tick)
            time.sleep(0.25)


    def disconnect(self):
        logging.debug("Disconnecting")
        self.kill = True
