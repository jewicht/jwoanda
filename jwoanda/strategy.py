import copy
from abc import ABCMeta, abstractmethod
import logging
from six import with_metaclass
from datetime import datetime

import numpy as np

from jwoanda.enums import Granularity
from jwoanda.portfolio.portfolio import Portfolio
from jwoanda.portfolio.btportfolio import BTPortfolio
from jwoanda.instenum import Instruments
from jwoanda.enums import TradeDirection, ExitReason


def minmax(instrument, value):
    return min(max(instrument.minimumTradeSize, value), instrument.maximumOrderUnits)


class BaseStrategy(with_metaclass(ABCMeta)):
    """Abstract Base Strategy class"""

    def __init__(self, name, **kwargs):
        self._name = name

        self._portfolio = BTPortfolio()

        self._options = {}

        self.options['trailingstop'] = kwargs.get("trailingstop", 0.)
        self.options['takeprofit'] = kwargs.get("takeprofit", 0.)
        self.options['stoploss'] = kwargs.get("stoploss", 0.)
        self.options['lifetime'] = kwargs.get("lifetime", 0.)
        
        self.options.update(kwargs)

        self._hm = None


    @property
    def time(self):
        return self.hm.currtime()

    @property
    def dayoftheweek(self):
        return datetime.fromtimestamp(self.time).isoweekday()

    @property
    def hour(self):
        return datetime.fromtimestamp(self.time).hour

    @property
    def minute(self):
        return datetime.fromtimestamp(self.time).minute
        
    def lasttick(self, instrument):
        return (self._portfolio.time(instrument),
                self._portfolio.bid(instrument),
                self._portfolio.ask(instrument))
        
    # def time(self, instrument):
    #     return self._portfolio.time(instrument)

    def bid(self, instrument):
        return self._portfolio.bid(instrument)

    def ask(self, instrument):
        return self._portfolio.ask(instrument)

    def getcandles(self, instrument, granularity, count):
        return self.hm.getcandles(instrument, granularity, count)
    
    @property
    def name(self):
        return self._name

    @property
    def options(self):
        return self._options

    def showoptions(self):
        logging.info("options:")
        for key, value in sorted(self.options.items()):
            logging.info("     {} = {}".format(key, value))

    @property
    def portfolio(self):
        return self._portfolio

    @portfolio.setter
    def portfolio(self, value):
        self._portfolio = value

    @property
    def hm(self):
        return self._hm

    @hm.setter
    def hm(self, __hm):
        self._hm = __hm

    @property
    def takeprofit(self):
        return self.options['takeprofit']

    @takeprofit.setter
    def takeprofit(self, value):
        self.options['takeprofit'] = value

    @property
    def stoploss(self):
        return self.options['stoploss']

    @stoploss.setter
    def stoploss(self, value):
        self.options['stoploss'] = value

    @property
    def trailingstop(self):
        return self.options['trailingstop']

    @trailingstop.setter
    def trailingstop(self, value):
        self.options['trailingstop'] = value

    def calcIndicators(self, candles):
        pass

    def calcMVA(self):
        pass


    def calcTP(self, takeprofit, instrument, units):
        if takeprofit > 0.:
            if units > 0:
                return self.ask(instrument) + takeprofit * instrument.pip
            else:
                return self.bid(instrument) - takeprofit * instrument.pip
        return 0.


    def calcSL(self, stoploss, instrument, units):
        if stoploss > 0.:
            if units > 0:
                return self.ask(instrument) - stoploss * instrument.pip
            else:
                return self.bid(instrument) + stoploss * instrument.pip
        return 0.


    def openposition(self, instrument, units, **kwargs):
        #pip to price
        stoploss = kwargs.get("stoploss", self.options['stoploss'])
        takeprofit = kwargs.get("takeprofit", self.options['takeprofit'])
        trailingstop = kwargs.get("trailingstop", self.options['trailingstop'])
        lifetime = kwargs.get("lifetime", self.options['lifetime'])
        newargs = {}
        if stoploss > 0.:
            newargs['stoploss'] = self.calcSL(stoploss, instrument, units)
        if takeprofit > 0.:
            newargs['takeprofit'] = self.calcTP(takeprofit, instrument, units)
        if trailingstop > 0.:
            newargs['trailingstop'] = trailingstop
        if lifetime > 0.:
            newargs['lifetime'] = lifetime

        return self._portfolio.openposition(self.name,
                                            instrument,
                                            units,
                                            **newargs)


    def closeposition(self, instrument, tradeID=None, reason=ExitReason.NORMAL):
        if tradeID is None:
            self._portfolio.closeallpositions(reason, instrument=instrument)
        else:
            self._portfolio.closeposition(tradeID, reason)


    def positionsize(self, instrument, maxrisk, td):

        if maxrisk <= 0. or maxrisk > 0.1:
            logging.error("maxrisk is not valid")
            return instrument.minimumTradeSize

        if (td != TradeDirection.LONG) and (td != TradeDirection.SHORT):
            logging.error("TradeDirection is not valid")
            return instrument.minimumTradeSize
        
        
        balance = self.portfolio.account.balance
        currency = self.portfolio.account.currency

        if balance < 0.:
            logging.error("You ran out of money")
            return instrument.minimumTradeSize
        
        maxLongLossinPips = self.options.get('maxLongLossinPips')
        maxShortLossinPips = self.options.get('maxShortLossinPips')

        if maxLongLossinPips is None or maxShortLossinPips is None:
            logging.warning("Can't find maxLong/ShortLossinPips")
            return instrument.minimumTradeSize

        if maxLongLossinPips <= 0. or maxShortLossinPips <= 0.:
            return instrument.minimumTradeSize

        if currency not in instrument.name:
            logging.error("The account currency is not in the pair")
            return instrument.minimumTradeSize

        if td == TradeDirection.LONG:
            return int(minmax(instrument, (balance * maxrisk) / (maxLongLossinPips * instrument.pip)))
        else:
            return int(minmax(instrument,(balance * maxrisk) / (maxShortLossinPips * instrument.pip)))


    def marginCalculator(self, instrument, units):
        accountcurr = self.portfolio.account.currency
    
        l = instrument.name.split('_')
        if len(l) != 2:
            return -1
    
        if accountcurr == l[0]:
            return units * instrument.marginRate
        elif accountcurr == l[1]:
            return units * self.ask(instrument) * instrument.marginRate
        else:
            # need to find accountcurr vs l[0] pair
            for instr in Instruments:
                if accountcurr in instr.name and l[0] in instr.name:
                    return self.marginCalculator(instr, units)
            return -1

    @staticmethod
    def crossabove(ma1, ma2):
        if (isinstance(ma2, float) or isinstance(ma2, np.float)):
            ma2p = ma2
            ma2pp = ma2
        else:
            ma2p = ma2[-1]
            ma2pp = ma2[-2]
            
        if (ma1[-1] > ma2p) and (ma1[-2] < ma2pp):
            return True
        else:
            return False
        
    @staticmethod
    def crossbelow(ma1, ma2):
        if (isinstance(ma2, float) or isinstance(ma2, np.float)):
            ma2p = ma2
            ma2pp = ma2
        else:
            ma2p = ma2[-1]
            ma2pp = ma2[-2]
            
        if (ma1[-1] < ma2p) and (ma1[-2] > ma2pp):
            return True
        else:
            return False


class Strategy(with_metaclass(ABCMeta, BaseStrategy)):
    """class to run single currency strategy"""
    def __init__(self, name, instruments, granularity, **kwargs):
        super(Strategy, self).__init__(name, **kwargs)

        if isinstance(instruments, Instruments):
            instruments = [instruments]

        for instrument in instruments:
            if not isinstance(instrument, Instruments):
                raise Exception("instrument needs to be an Instruments and not {}".format(type(instrument)))

        if not isinstance(granularity, Granularity):
            raise Exception("Did not understood granularity. Type={}".format(type(granularity)))


        self._instruments = instruments
        self._granularity = granularity
            
        self._units = kwargs.get('units', self.instrument.minimumTradeSize)

        s = ", ".join([i.name for i in instruments])
        s += "@ {}".format(granularity.name)            
        logging.info("init {} on {}".format(self.name, s))
        

    @property
    def fullname(self):
        s = self.name
        s +=  ",".join(self.instruments)
        s += "@{}".format(self.granularity)
        return s


    @property
    def instrument(self):
        return self._instruments[0]

    @property
    def instruments(self):
        return self._instruments

    @property
    def granularity(self):
        return self._granularity

    @property
    def units(self):
        return self._units

    @abstractmethod
    def onTick(self):
        pass

    @abstractmethod
    def onCandle(self):
        pass


class TickStrategy(with_metaclass(ABCMeta, BaseStrategy)):
    """class to run single currency strategy on ticks"""

    def __init__(self, name, instrument, **kwargs):
        if not isinstance(instrument, Instruments):
            raise Exception("instrument needs to be an Instruments and not {}".format(type(instrument)))

        self._instrument = instrument
        self._units = kwargs.get('units', instrument.minimumTradeSize)

        super(TickStrategy, self).__init__(name, **kwargs)

    @property
    def granularity(self):
        return Granularity.NONE
        
    @property
    def fullname(self):
        return '-'.join([self.name, self.instrument.name])

    @property
    def instrument(self):
        return self._instrument

    @property
    def instruments(self):
        return [self.instrument]

    @property
    def units(self):
        return self._units

    @abstractmethod
    def onTick(self, tick):
        pass



