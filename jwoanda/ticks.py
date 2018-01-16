try:
    import lzma
except ImportError:
    from backports import lzma
try:
    import cPickle as pickle
except:
    import pickle
import numpy as np


from jwoanda.instenum import Instruments


class Ticks(object):
    def __init__(self, instrument, size=1000, nparr=None):

        if isinstance(instrument, Instruments):
            self._instrument = instrument
        else:
            raise Exception("Not a valid instrument: type={}".format(type(instrument)))

        if nparr is not None:
            self._data = nparr
            self._nticks = len(nparr)
            return

        self._data = self.zerodata(size)
        self._nticks = 0


    def zerodata(self, size):
        return np.zeros(size, dtype=[('time', np.float64),
                                     ('bid', np.float64),
                                     ('ask', np.float64)])


    @property
    def instrument(self):
        return self._instrument


    @property
    def data(self):
        return self._data


    # @instrument.setter
    # def instrument(self, value):
    #     self._instrument = value


    @property
    def nticks(self):
        return self._nticks


    # @nticks.setter
    # def nticks(self, value):
    #     self._nticks = value


    def set(self, index, tick):
        if index >= len(self._data):
            self._data = np.append(self._data, self.zerodata(len(self._data)))
        self._data[index] = tick


    def add(self, tick):
        self.set(self._nticks, tick)
        self._nticks += 1


    def filled(self):
        return self._data[0:self.nticks - 1]


    def head(self, newsize, inplace=False):
        if newsize > self._data.size:
            newsize = self._data.size

        reqticks = self._data[:newsize]

        if not inplace:
            return Ticks(instrument=self.instrument, nparr=reqticks)
        else:
            self._data = reqticks


    def tail(self, size, inplace=False):
        if size > self.nticks:
            size = self.nticks

        reqticks = self._data[self.nticks - size:self.nticks]

        if not inplace:
            return Ticks(instrument=self.instrument, nparr=reqticks)
        else:
            self._data = reqticks


    def load(self, filename):
        f = lzma.open(filename, mode='rb')
        data = pickle.load(f)
        f.close()
        self._data = data['ticks']
        self._nticks = data['nticks']
        self._instrument = data['instrument']


    def save(self, filename):
        data = {}
        data['ticks'] = self._data
        data['nticks'] = self._nticks
        data['instrument'] = self._instrument
        f = lzma.open(filename, mode='wb')
        pickle.dump(data, f)
        f.close()



class MultiTicks(object):
    def __init__(self, instruments, size=1000):
        self._ticks = {}
        self._instruments = instruments
        for instrument in instruments:
            if not isinstance(instrument, Instruments):
                raise Exception('Please provide a proper instrument')
        
            self._ticks[instrument] = Ticks(instrument=instrument, size=size)


    @property
    def instruments(self):
        return self._instruments


    def ticks(self, instrument):
        #print(type(instrument))
        return self._ticks[instrument]


    def nticks(self, instrument):
        return self._ticks[instrument].nticks


    def tail(self, size, inplace=False):
        nticks = self._ticks[self._instruments[0]].nticks
        if size > nticks:
            size = nticks

        tmp = {}#MultiTicks(self._instruments)
        for instrument in self._instruments:
            tmp[instrument] = self._ticks[instrument].tail(size)

        if not inplace:
            return tmp
        else:
            self._ticks = tmp
