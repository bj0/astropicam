import numpy as np


def _map_val(i, low, high, dx, b):
    if i <= low:
        return 0
    elif i >= high:
        return 255
    else:
        return dx * i + b


_map_val = np.vectorize(_map_val, otypes=['ubyte'])


def linear_stretch(buf):
    median = np.median(buf)
    std = np.std(buf)
    low = median - 2.5 * std
    high = median + 5.0 * std
    dx = 255 / (high - low)
    b = -dx * low

    table = _map_val(np.arange(0, 256, dtype='ubyte'), low, high, dx, b)

    return table[buf]


try:
    from .cmaths import stretchrgb
    from .cmaths import stretch
except ImportError as e:
    print("fallback", e)
    stretch = linear_stretch


def main():
    # speed test stretch
    import timeit

    N = 1000
    print(timeit.timeit('_stretch(buf)',
                        setup='import numpy; from __main__ import linear_stretch; buf = numpy.frombuffer(numpy.random.bytes(320*240), dtype="ubyte")',
                        number=N) / N)

    print(timeit.timeit('stretch(buf)',
                        setup='import numpy; from picam.cmaths import stretch; buf = numpy.random.bytes(320*240*3)',
                        number=N) / N)
    print(timeit.timeit('stretch(buf)',
                        setup='import numpy; from picam.cmaths import stretch; buf = numpy.random.bytes(320*240)',
                        number=N) / N)
    print(timeit.timeit('stretchrgb(buf)',
                        setup='import numpy; from picam.cmaths import stretchrgb; buf = numpy.random.bytes(320*240*3)',
                        number=N) / N)


if __name__ == '__main__':
    main()
