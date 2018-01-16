import copy
from abc import ABCMeta, abstractmethod
import logging
from six import with_metaclass

from jwoanda.enums import Granularity, VolumeGranularity
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

        self.options.update(kwargs)
        
        self._mincandles = kwargs.get("mincandles", 1)
        self._minticks = kwargs.get("minticks", 1)
        self._reqcandles = kwargs.get("reqcandles", 500)
        self._reqticks = kwargs.get("reqticks", 1000)


    def time(self, instrument):
        return self._portfolio.time(instrument)

    def bid(self, instrument):
        return self._portfolio.bid(instrument)

    def ask(self, instrument):
        return self._portfolio.ask(instrument)

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
    def reqticks(self):
        return self._reqticks

    @reqticks.setter
    def reqticks(self, value):
        self._reqticks = value

    @property
    def reqcandles(self):
        return self._reqcandles

    @reqcandles.setter
    def reqcandles(self, value):
        self._reqcandles = value

    @property
    def minticks(self):
        return self._minticks

    @minticks.setter
    def minticks(self, value):
        self._minticks = value

    @property
    def mincandles(self):
        return self._mincandles

    @mincandles.setter
    def mincandles(self, value):
        self._mincandles = value

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
        newargs = {}
        if stoploss > 0.:
            newargs['stoploss'] = self.calcSL(stoploss, instrument, units)
        if takeprofit > 0.:
            newargs['takeprofit'] = self.calcTP(takeprofit, instrument, units)
        if trailingstop > 0.:
            newargs['trailingstop'] = trailingstop
            
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



class Strategy(with_metaclass(ABCMeta, BaseStrategy)):
    """class to run single currency strategy"""
    def __init__(self, name, instrument, granularity, **kwargs):
        if not isinstance(instrument, Instruments):
            raise Exception("instrument needs to be an Instruments and not {}".format(type(instrument)))

        self._volmode = False
        if isinstance(granularity, Granularity):
            self._granularity = granularity
        elif isinstance(granularity, VolumeGranularity):
            self._granularity = granularity
            self._volmode = True
        else:
            raise Exception("Did not understood granularity. Type={}".format(type(granularity)))
        self._instrument = instrument
        self._units = kwargs.get('units', instrument.minimumTradeSize)
        super(Strategy, self).__init__(name, **kwargs)

        logging.info("init %s on %s @ %s",
                     self.name,
                     self.instrument.name,
                     self.granularity.name)
    @property
    def fullname(self):
        return '-'.join([self.name, self.instrument.name, self.granularity.name])

    @property
    def instrument(self):
        return self._instrument

    @property
    def instruments(self):
        return [self.instrument]

    @property
    def granularity(self):
        return self._granularity

    @property
    def units(self):
        return self._units

    @abstractmethod
    def onTick(self, candles, cnt):
        pass

    @abstractmethod
    def onCandle(self, candles, cnt):
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



class MultiInstrumentsStrategy(with_metaclass(ABCMeta, BaseStrategy)):
    """class to run multiple currencies strategy"""
    def __init__(self, name, instruments, granularity, **kwargs):
        """MultiInstrumentsStrategy constructor
        inputs:
              name: string
              instruments: List of Instruments
              granularity: Granularity object
        """
        super(MultiInstrumentsStrategy, self).__init__(name, **kwargs)

        for instrument in instruments:
            if not isinstance(instrument, Instruments):
                raise Exception("instrument needs to be an Instruments and not {}".format(type(instrument)))

        self._instruments = instruments

        self._volmode = False
        if isinstance(granularity, Granularity):
            self._granularity = granularity
        else:
            raise Exception("Did not understood granularity. Type={}".format(type(granularity)))

    @property
    def fullname(self):
        _instruments = '-'.join([instrument.name for instrument in self.instruments])
        return '-'.join([self.name, _instruments, self.granularity.name])

    @property
    def instruments(self):
        return self._instruments

    @property
    def granularity(self):
        return self._granularity

    @abstractmethod
    def onMultiCandle(self, candles, cnt):
        """method is called at the close. Candles is a dictionary containing the Candles"""
        pass



class MultiGranularitiesStrategy(with_metaclass(ABCMeta, BaseStrategy)):
    """ class to run over multiple granularites"""

    def __init__(self, name, instrument, granularities, **kwargs):
        """MultiGranularitiesStrategy constructor
        inputs:
              name: string
              instrument: Instruments
              granularities: List of Granularity object
        """
        super(MultiGranularitiesStrategy, self).__init__(name, **kwargs) 
        self._instrument = instrument
        self._granularities = granularities
        
    @property
    def instrument(self):
        return self._instruments

    @property
    def granularities(self):
        return self._granularities

    @abstractmethod
    def onTick(self, candles, cnt):
        pass

    @abstractmethod
    def onCandle(self, candles, cnt):
        pass
