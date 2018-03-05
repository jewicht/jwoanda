import logging
import threading

from jwoanda.enums import Events
from jwoanda.strategy import Strategy, TickStrategy


class StrategyTrading(threading.Thread):
    def __init__(self, strategy, evr):
        super(StrategyTrading, self).__init__(name="_".join(["StrategyTrading", strategy.name]))
        self.kill = False
        self.strategy = strategy
        self.evr = evr


    def run(self):
        stop = threading.Event()
        while not self.kill:
            self.evr.wait()
            if self.kill:
                return

            marketopen = True
            for i in self.strategy.instruments:
                if not self.strategy.portfolio.istradeable(i):
                    marketopen = False
                    break

            if not marketopen:
                continue
            
            try:
                self.strategy.onCandle()
            except:
                logging.exception("your strategy crashed in onCandle")
            stop.wait(1)


    def disconnect(self):
        self.kill = True
        self.evr.set()



class TickStrategyTrading(threading.Thread):
    def __init__(self, strategy, tickQueue):
        super(TickStrategyTrading, self).__init__(name="_".join(["StrategyTrading", strategy.name]))
        self.kill = False
        self.strategy = strategy
        self.tickQueue = tickQueue


    def run(self):
        while not self.kill:
            e = self.tickQueue.get()
            if e['type'] == Events.TICK:
                tick = e['tick']
                if not self.strategy.portfolio.istradeable(tick[0]):
                    continue
                
                try:
                    self.strategy.onTick(tick)
                except:
                    logging.exception("your strategy crashed in onTick")
            elif e['type'] == Events.KILL:
                self.kill = True
                break
            else:
                pass


    def disconnect(self):
        self.kill = True
        self.tickQueue.put({'type': Events.KILL})
