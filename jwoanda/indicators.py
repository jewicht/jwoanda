from __future__ import print_function

import talib as ta
import numpy as np
from jwoanda.numpyfcn import nans
import pandas as pd

def shift(xs, n):
    e = np.empty_like(xs)
    if n >= 0:
        e[:n] = np.nan
        e[n:] = xs[:-n]
    else:
        e[n:] = np.nan
        e[:n] = xs[-n:]
    return e

def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def buildLaggedFeatures(s, colnames, lags, dropna=False):
    '''
    Builds a new DataFrame to facilitate regressing over all possible lagged features
    '''
    if type(s) is pd.DataFrame:
        new_dict = {}
        for col_name in s:
            new_dict[col_name] = s[col_name]
        for col_name in colnames:
            # create lagged Series
            for l in lags:
                new_dict['%slag%d' %(col_name, l)] = s[col_name].shift(l)
        res = pd.DataFrame(new_dict, index=s.index)
    # elif type(s) is pd.Series:
    #     the_range=lags
    #     res=pd.concat([s.shift(i) for i in the_range],axis=1)
    #     res.columns=['lag_%d' %i for i in the_range]
    else:
        print('Only works for DataFrame')
        return None
    if dropna:
        return res.dropna()
    else:
        return res 

def diffpad(input, a):
    return np.pad(np.diff(input, n=a), [a, 0], mode='constant', constant_values=[float('nan'), 0])

def diffpadDF(input, price, timeperiod):
    return np.pad(np.diff(input[price], n=timeperiod), [timeperiod, 0], mode='constant', constant_values=[float('nan'), 0])

# WMA( 2 WMA(t/2) - WMA(t), sqrt(t))    
# def TASlopeDir(input, timeperiod):
#     wma1=ta.WMA(input, timeperiod=int(timeperiod/2))
#     wma2=ta.WMA(input, timeperiod=timeperiod)
#     wma1=2.*wma1-wma2
#     wma1=ta.WMA(wma1, timeperiod=int(np.sqrt(timeperiod)))
#     return wma1

def TASlopeDir(input, timeperiod, price):
    wma1 = ta.WMA(input[price], timeperiod=int(timeperiod/2))
    wma2 = ta.WMA(input[price], timeperiod=timeperiod)
    wma1 = 2. * wma1 - wma2
    wma1 = ta.WMA(wma1, timeperiod=int(np.sqrt(timeperiod)))
    return wma1

def TADiffSlopeDirDF(input, timeperiod, price):
    wma1 = ta.WMA(input[price].values, timeperiod=int(timeperiod/2))
    wma2 = ta.WMA(input[price].values, timeperiod=timeperiod)
    wma1 = 2.*wma1-wma2
    wma1 = ta.WMA(wma1, timeperiod=int(np.sqrt(timeperiod)))
    wma1 = diffpad(wma1, 1)
    return wma1



def myzigzag(pivots):
    pivlocations = np.where(np.abs(pivots))[0]
    output = nans(pivlocations[0])
    for i in range(0, len(pivlocations)-1):
        s = pivlocations[i]
        f = pivlocations[i+1]
        #output = np.append(output, np.linspace(pivots[s], pivots[f], num=f-s, endpoint=False))
        output = np.append(output, np.linspace(pivots[s], 0., num=f-s, endpoint=True)) 
    output = np.append(output, [pivots[pivlocations[len(pivlocations)-1]]])
    if len(output) != len(pivots):
        output = np.append(output, nans(len(pivots)-pivlocations[len(pivlocations)-1]))
    return output
