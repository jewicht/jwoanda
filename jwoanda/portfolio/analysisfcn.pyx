cimport cython

import numpy as np
cimport numpy as np

ctypedef np.float64_t FLOAT_t

@cython.boundscheck(False)
@cython.wraparound(False)
def drawdown(np.ndarray[FLOAT_t, ndim=1] pl):
    cdef long maxsuccloss = -1
    cdef long maxsuccwin = -1
    cdef double maxdrawdown = 1

    cdef long currsuccloss = 0
    cdef long currsuccwin = 0
    cdef double currdrawdown = 0
    
    cdef long i
    for i in range(0, pl.size):
        if pl[i] == 0.:
            continue
        if pl[i] > 0.:
            if currsuccloss > maxsuccloss:
                maxsuccloss = currsuccloss
            currsuccloss = 0
            currsuccwin += 1
            currdrawdown = 0.
        else:
            if currsuccwin > maxsuccwin:
                maxsuccwin = currsuccwin
            currsuccwin = 0
            currsuccloss += 1
            currdrawdown += pl[i]
            if currdrawdown < maxdrawdown:
                maxdrawdown = currdrawdown
    
    if currsuccloss > maxsuccloss:
        maxsuccloss = currsuccloss
    if currsuccwin > maxsuccwin:
        maxsuccwin = currsuccwin        
    return maxsuccloss, maxsuccwin, maxdrawdown
