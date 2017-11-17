cimport cython

import numpy as np
cimport numpy as np

ctypedef np.float64_t FLOAT_t
ctypedef np.uint8_t BOOL_t

@cython.boundscheck(False)
@cython.wraparound(False)
def resizebyvolume_cython(candles, long maxvolume):

    cdef np.ndarray[FLOAT_t, ndim=1] oa = candles.data['openAsk']
    cdef np.ndarray[FLOAT_t, ndim=1] ob = candles.data['openBid']
    cdef np.ndarray[FLOAT_t, ndim=1] ha = candles.data['highAsk']
    cdef np.ndarray[FLOAT_t, ndim=1] hb = candles.data['highBid']
    cdef np.ndarray[FLOAT_t, ndim=1] la = candles.data['lowAsk']
    cdef np.ndarray[FLOAT_t, ndim=1] lb = candles.data['lowBid']
    cdef np.ndarray[FLOAT_t, ndim=1] ca = candles.data['closeAsk']
    cdef np.ndarray[FLOAT_t, ndim=1] cb = candles.data['closeBid']
    cdef np.ndarray[FLOAT_t, ndim=1] vol = candles.data['volume']
    cdef np.ndarray[BOOL_t, ndim=1] complete = candles.data['complete'].astype(np.uint8)
    cdef np.ndarray[FLOAT_t, ndim=1] opentime = candles.data['time']

    cdef long totvolume = vol.sum()
    cdef long maxentries = int(1.2 * totvolume / maxvolume)
    
    cdef float volume = 0
    cdef long iv = 0
    
    cdef double openAsk = 0.
    cdef double openBid = 0.
    cdef double highAsk = 0.
    cdef double highBid = 0.
    cdef double lowAsk = 0.
    cdef double lowBid = 0.
    cdef double closeAsk = 0.
    cdef double closeBid = 0.
    cdef double openTime = 0.

    cdef np.ndarray[FLOAT_t, ndim=1] vopentime = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] voa = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vob = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vha = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vhb = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vla = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vlb = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vca = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vcb = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[FLOAT_t, ndim=1] vvol = np.zeros(maxentries, dtype=np.float64)
    cdef np.ndarray[BOOL_t, ndim=1] vcomplete = np.zeros(maxentries, dtype=np.uint8)

    cdef long i = 0
    for i in range(0, oa.size):

        if not complete[i]:
            continue
        
        if volume == 0:
            openTime = opentime[i]
            openAsk = oa[i]
            openBid = ob[i]
            highAsk = ha[i]
            highBid = hb[i]
            lowAsk = la[i]
            lowBid = lb[i]
            closeAsk = ca[i]
            closeBid = cb[i]

        volume += vol[i]

        if ha[i] > highAsk:
            highAsk = ha[i]
        if hb[i] > highBid:
            highBid = hb[i]
        if la[i] < lowAsk:
            lowAsk = la[i]
        if lb[i] < lowBid:
            lowBid = lb[i]

        if volume >= maxvolume:
            closeAsk = ca[i]
            closeBid = cb[i]

            vopentime[iv] = openTime
            voa[iv] = openAsk
            vob[iv] = openBid
            vha[iv] = highAsk
            vhb[iv] = highBid
            vla[iv] = lowAsk
            vlb[iv] = lowBid
            vca[iv] = closeAsk
            vcb[iv] = closeBid
            vvol[iv] = volume
            vcomplete[iv] = True
            
            volume = 0
            iv += 1

    if volume > 0:
        vopentime[iv] = openTime
        voa[iv] = openAsk
        vob[iv] = openBid
        vha[iv] = highAsk
        vhb[iv] = highBid
        vla[iv] = lowAsk
        vlb[iv] = lowBid
        vca[iv] = closeAsk
        vcb[iv] = closeBid
        vvol[iv] = volume
        vcomplete[iv] = False
        iv += 1

    vopentime = vopentime[0:iv]
    vob = vob[0:iv]
    vhb = vhb[0:iv]
    vlb = vlb[0:iv]
    vcb = vcb[0:iv]
    voa = voa[0:iv]
    vha = vha[0:iv]
    vla = vla[0:iv]
    vca = vca[0:iv]
    vvol = vvol[0:iv]
    vcomplete = vcomplete[0:iv]

    cdict = {}
    cdict['openBid'] = vob
    cdict['highBid'] = vhb
    cdict['lowBid'] = vlb
    cdict['closeBid'] = vcb
    
    cdict['openAsk'] = voa
    cdict['highAsk'] = vha
    cdict['lowAsk'] = vla
    cdict['closeAsk'] = vca
    
    cdict['volume'] = vvol
    cdict['time'] = vopentime
    cdict['complete'] = vcomplete
    
    return cdict
