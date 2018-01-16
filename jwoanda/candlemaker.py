import threading
from threading import Event
import multiprocessing
import logging
from datetime import datetime

try:
    from queue import Queue
except:
    from Queue import Queue

from jwoanda.history import HistoryManager, floattostr
from jwoanda.candles import MultiCandles
from jwoanda.ticks import MultiTicks
from jwoanda.enums import Granularity, VolumeGranularity, Events
from jwoanda.strategy import TickStrategy, MultiInstrumentsStrategy
from jwoanda.strategytrading import StrategyTrading, MultiStrategyTrading, TickStrategyTrading
from jwoanda.oandaaccount import oandaenv

class CandleMakerHelper(object):
    def __init__(self, tickQueue, strategy, **kwargs):

        self.kill = False
        self.stop = Event()
        self.volmode = False

        self.strategy = strategy
        self.gran = strategy.granularity
        self.instruments = strategy.instruments

        self.tickQueue = tickQueue

        self.tickmode = (self.gran == Granularity.NONE)
        self.name = kwargs.get('name')


    def createThreads(self):
        if isinstance(self.gran, Granularity):
            self.period = self.gran.value
            self.cmt = CandleMakerThread(self.strategy,
                                         self.tickQueue,
                                         name=self.name.replace('Helper', ''))
        elif isinstance(self.gran, VolumeGranularity):
            self.volmode = True
            if len(self.instruments) > 1:
                raise Exception("Too many instruments for volume mode")

            self.cmt = CandleMakerThread(self.strategy,
                                         self.tickQueue,
                                         name=self.name.replace('Helper', ''))
        else:
            raise Exception("Do not understand granularity")


    def run(self):

        self.cmt.start()

        while not self.kill:

            timetowait = 10
            if not self.volmode and not self.tickmode:
                now = datetime.now()
                seconds_since_midnight = (now - now.replace(hour=0,
                                                            minute=0,
                                                            second=0,
                                                            microsecond=0)).total_seconds()
                #sleep(self.period - (seconds_since_midnight % self.period))
                timetowait = self.period - (seconds_since_midnight % self.period)
            self.stop.wait(timetowait)
            if self.kill:
                return
            if not self.volmode and not self.tickmode:
                self.cmt.makeCandle()

            if not self.cmt.isAlive():
                logging.error("Candle maker thread died, quitting")
                self.disconnect()


    def disconnect(self):
        self.tickQueue.put(Events.KILL)
        self.cmt.disconnect()
        self.kill = True
        self.stop.set()



class CandleMakerHelperThread(threading.Thread):
    def __init__(self, tickQueue, strategy, **kwargs):
        threading.Thread.__init__(self, name=kwargs.get('name'))
        self.cmh = CandleMakerHelper(tickQueue, strategy, name=kwargs.get('name'))
        self.cmh.createThreads()


    def run(self):
        self.cmh.run()


    def disconnect(self):
        self.cmh.disconnect()



class CandleMakerHelperProcess(multiprocessing.Process):
    def __init__(self, tickQueue, strategy, **kwargs):
        multiprocessing.Process.__init__(self, name=kwargs.get('name'))
        self.tickQueue = tickQueue
        self.strategy = strategy
        self.cmh = None

    def run(self):
        self.cmh = CandleMakerHelper(self.tickQueue, self.strategy, name=self.name)
        self.cmh.createThreads()
        self.cmh.run()


    def disconnect(self):
        if self.cmh is not None:
            self.cmh.disconnect()



class CandleMakerThread(threading.Thread):
    def __init__(self, strategy, tickQueue, resumefromhistory=True, **kwargs):
        super(CandleMakerThread, self).__init__(**kwargs)
        self.strategy = strategy
        self.portfolio = strategy.portfolio
        self.tickQueue = tickQueue
        self.instruments = strategy.instruments
        self.granularity = strategy.granularity
        self.kill = False
        self.resumefromhistory = resumefromhistory

        self.volmode = False
        if isinstance(self.granularity, VolumeGranularity):
            self.volmode = True
            self.maxvolume = self.granularity.volume
            

        self.tickmode = (self.granularity == Granularity.NONE)
        if not self.tickmode:
            self.mcandles = MultiCandles(instruments=self.instruments, granularity=self.granularity, size=10)
            #        else:
            #            self.ticks = MultiTicks(instruments=self.instruments, size=1000000)
        self.iC = 0

        if isinstance(self.strategy, TickStrategy):
            self.tt = TickStrategyTrading(self.strategy,
                                          self,
                                          name='_'.join(["Trading", self.strategy.name]))
        elif isinstance(self.strategy, MultiInstrumentsStrategy):
            self.tt = MultiStrategyTrading(self.strategy,
                                           self,
                                           name='_'.join(["Trading", self.strategy.name]))
        else:
            self.tt = StrategyTrading(self.strategy,
                                      self,
                                      name='_'.join(["Trading", self.strategy.name]))




    def gethistory(self):
        #get history and resume from there
        for instrument in self.instruments:
            if not self.volmode:
                candles = HistoryManager.downloadcandles(instrument.name, self.granularity.name, 200)


                if candles is not None:
                    logging.info("We received %d candles", len(candles))
                    self.mcandles.candles(instrument).fill(candles)

                else:
                    logging.error("We couldn't get history!")

            else:
                #download last day data
                end_date = float(datetime.utcnow().strftime("%s"))
                start_date = end_date - 3. * 24 * 60 * 60
                end_date += 24 * 60 * 60
                candles = HistoryManager.downloadhistoricaldata(instrument, Granularity.S5, start_date, end_date, showpbar=False)
                #candles = HistoryManager.downloadcandles(instrument.name, Granularity.S5.name, 5000)

                if candles is not None:
                    logging.info("We received %d candles", candles.ncandles)

                    #tmp = Candles(instrument=instrument, granularity=Granularity.S5, size=100000)
                    #tmp.fill(candles)

                    tmp = HistoryManager.resizebyvolume(candles, self.maxvolume)
                    tmp.resize(100000)

                    self.mcandles = MultiCandles(clist=[tmp])

                else:
                    logging.error("We couldn't get history!")


        #resume from history
        #last candle should not be completed
        ncandles = self.mcandles.candles(self.instruments[0]).ncandles
        lastcandle = self.mcandles.candles(self.instruments[0]).data[ncandles - 1]
        if not lastcandle["complete"]:
            for instrument in self.instruments:
                self.mcandles.candles(instrument).ncandles -= 1
            self.iC = self.mcandles.candles(self.instruments[0]).ncandles
        else:
            logging.warning("Last candle was complete, is the market open?")
            self.iC = self.mcandles.candles(instrument).ncandles

        for instrument in self.instruments:
            logging.info("We now have %d %s candles", self.mcandles.candles(instrument).ncandles, instrument.name)


    def addTick(self, tick):
        instrument, time, bid, ask = tick

        logging.debug("%s time=%s bid=%s spread=%s ",
                      instrument.name,
                      datetime.fromtimestamp(time),
                      floattostr(bid, instrument.displayPrecision),
                      floattostr(ask-bid, instrument.displayPrecision))

        if self.tickmode:
            #self.ticks.ticks(instrument).add((time, bid, ask))
            self.tt.tickEvent((time, bid, ask))
            return

        if self.iC >= len(self.mcandles.candles(instrument).data):
            self.mcandles.resize(int(len(self.mcandles.candles(instrument).data) * 1.5))
        
        thiscandle = self.mcandles.candles(instrument).data[self.iC]

        if thiscandle['volume'] == 0.:
            thiscandle['openAsk'] = thiscandle['highAsk'] = thiscandle['lowAsk'] = thiscandle['closeAsk'] = ask
            thiscandle['openBid'] = thiscandle['highBid'] = thiscandle['lowBid'] = thiscandle['closeBid'] = bid
            thiscandle['time'] = time
        else:
            if ask > thiscandle['highAsk']:
                thiscandle['highAsk'] = ask
            if ask < thiscandle['lowAsk']:
                thiscandle['lowAsk'] = ask
            if bid > thiscandle['highBid']:
                thiscandle['highBid'] = bid
            if bid < thiscandle['lowBid']:
                thiscandle['lowBid'] = bid

            thiscandle['closeAsk'] = ask
            thiscandle['closeBid'] = bid

        thiscandle['volume'] += 1
        self.tt.tickEvent()

        if self.volmode:
            if thiscandle['volume'] >= self.maxvolume:
                self.makeCandle()


    def run(self):
        if not self.tickmode and self.resumefromhistory:
            self.gethistory()

        while not self.kill:
            tick = self.tickQueue.get()
            if self.kill or (tick == Events.KILL):
                return
            self.addTick(tick)


    def makeCandle(self):
        for instrument in self.instruments:
            currcandle = self.mcandles.candles(instrument).data[self.iC]
            if currcandle['volume'] == 0:
                logging.warning("Volume = 0 for instrument %s. Aborting", instrument.name)
                return

        for instrument in self.instruments:
            currcandle = self.mcandles.candles(instrument).data[self.iC]
            logging.debug("New %s candle:\n"
                          "openBid  %s  openAsk  %s\n"
                          "highBid  %s  highAsk  %s\n"
                          "lowBid   %s  lowAsk   %s\n"
                          "closeBid %s  closeAsk %s\n"
                          "volume   %s",
                          instrument.name,
                          floattostr(currcandle['openBid'], instrument.displayPrecision),
                          floattostr(currcandle['openAsk'], instrument.displayPrecision),
                          floattostr(currcandle['highBid'], instrument.displayPrecision),
                          floattostr(currcandle['highAsk'], instrument.displayPrecision),
                          floattostr(currcandle['lowBid'], instrument.displayPrecision),
                          floattostr(currcandle['lowAsk'], instrument.displayPrecision),
                          floattostr(currcandle['closeBid'], instrument.displayPrecision),
                          floattostr(currcandle['closeAsk'], instrument.displayPrecision),
                          floattostr(currcandle['volume'], 0))


            self.mcandles.candles(instrument).ncandles += 1

        self.tt.candleEvent()
        self.iC += 1


    def disconnect(self):
        self.kill = True
