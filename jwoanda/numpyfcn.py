import numpy as np

def shift(xs, n):
    e = np.empty_like(xs)
    if n >= 0:
        e[:n] = np.nan
        e[n:] = xs[:-n]
    else:
        e[n:] = np.nan
        e[:n] = xs[-n:]
    return e

def avec(shape, value, dtype=float):
    a = np.empty(shape, dtype)
    a.fill(value)
    return a

def nans(shape, dtype=float):
    return avec(shape, np.nan, dtype)


class tema(object):
    def __init__(self, decay):
        self.decay = decay
        self.prev = np.nan
        
    def get(self, value):
        if np.isnan(self.prev):
            self.prev = value
            return self.prev
        else:
            self.prev = value * self.decay + self.prev * (1. - self.decay)
            return self.prev
