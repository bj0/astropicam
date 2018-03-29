import numpy as np
cimport numpy as np

cdef struct Stats:
    """
    structure to hold image stats
    """
    double high, low, dx, b

cdef unsigned char mapval(unsigned char val, double high, double low, double dx, double b) nogil:
    """
    map a value to a range with slope and offset
    """
    if val <= low:
        return 0
    elif val >= high:
        return 255
    else:
        return <unsigned char>( dx*val + b)

cdef Stats calc_stats(np.ndarray[np.uint8_t, ndim=1] buf):
    cdef Stats out
    cdef double median = np.median(buf)
    cdef double std = np.std(buf)
    out.low = max(0, median - 2.5 * std)
    out.high = min(255, median + 5.0 * std)
    out.dx = 255 / (out.high - out.low)
    out.b = -out.dx * out.low
    return out


def stretch(bytes raw):
    """
    linear stretch (normalize?) of grayscale image data
    """
    cdef np.ndarray[np.uint8_t, ndim=1] buf = np.frombuffer(raw, dtype='ubyte')
    # create an output array
    cdef np.ndarray[np.uint8_t, ndim=1] out = np.empty((320*240,), dtype='ubyte')
    cdef int i, j=0
    cdef np.ndarray[np.uint8_t, ndim=1] input

    if len(buf) > 320*240:
        # full color array
        for i in range(0, len(buf), 3):
            out[j] = <unsigned char>( 0.299*buf[i] + 0.587*buf[i+1] + 0.114*buf[i+2])
            j += 1
        input = out
    else:
        # already grayscale
        input = buf

    cdef Stats stats = calc_stats(input)

    cdef unsigned char val
    for i in range(320*240):
        out[i] = mapval(input[i], stats.high, stats.low, stats.dx, stats.b)

    return out

def stretchrgb(bytes raw):
    """
    linear stretch (normalize?) of rgb data
    """
    cdef np.ndarray[np.uint8_t, ndim=1] buf = np.frombuffer(raw, dtype='ubyte')
    # create an output array
    cdef np.ndarray[np.uint8_t, ndim=1] out = np.empty_like(buf)

    cdef np.ndarray[np.uint8_t, ndim=1] bufr = buf[::3]
    cdef np.ndarray[np.uint8_t, ndim=1] bufg = buf[1::3]
    cdef np.ndarray[np.uint8_t, ndim=1] bufb = buf[2::3]

    cdef np.ndarray[np.uint8_t, ndim=1] outr = out[::3]
    cdef np.ndarray[np.uint8_t, ndim=1] outg = out[1::3]
    cdef np.ndarray[np.uint8_t, ndim=1] outb = out[2::3]

    cdef Stats statsr = calc_stats(bufr)
    cdef Stats statsg = calc_stats(bufg)
    cdef Stats statsb = calc_stats(bufb)

    cdef int i
    for i in range(320*240):
        outr[i] = mapval(bufr[i], statsr.high, statsr.low, statsr.dx, statsr.b)
        outg[i] = mapval(bufg[i], statsg.high, statsg.low, statsg.dx, statsg.b)
        outb[i] = mapval(bufb[i], statsb.high, statsb.low, statsb.dx, statsb.b)

    return out