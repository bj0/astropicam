import numpy as np
import cv2
from photutils import find_peaks


def _map_val(i, low, high, dx, b):
    if i <= low:
        return 0
    elif i >= high:
        return 255
    else:
        return dx * i + b


_map_val = np.vectorize(_map_val, otypes=['ubyte'])


def linear_stretch(buf):
    """
    simple linear stretch
    :param buf:
    :return:
    """
    median = np.median(buf)
    std = np.std(buf)
    low = median - 2.5 * std
    high = median + 5.0 * std
    dx = 255 / (high - low)
    b = -dx * low

    table = _map_val(np.arange(0, 256, dtype='ubyte'), low, high, dx, b)

    return table[buf]


def measure_lp(buf):
    """
    measure focus using Laplacian
    :param buf:
    :return:
    """
    im = np.frombuffer(buf, dtype=np.uint8).reshape((240, 320, 3))
    im = np.roll(im, 1, axis=-1)
    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def measure_fwhm(buf):
    """
    measure focus using FWHM (slow)
    :param buf:
    :return:
    """
    im = np.frombuffer(buf, dtype=np.uint8).reshape((240, 320, 3))
    fit = fit_2dgaussian(im[:, :, 1])
    # print(fit)
    f = sqrt(fit.x_stddev ** 2 + fit.y_stddev ** 2) * 2.3548200450309493
    # print('f=', f)
    return f


def measure_hfr(buf):
    """
    measure focus using HFR
    :param buf:
    :return:
    """
    im = np.frombuffer(buf, dtype=np.uint8).reshape((240, 320, 3))

    # sub background
    median = np.median(im[:, :, 1])
    Im = im[:, :, 1] - median

    # find star
    max = np.max(Im)
    tbl = find_peaks(Im, max - median, box_size=100, subpixel=False)
    x, y = int(tbl['x_peak'][0]), int(tbl['y_peak'][0])

    # improve center estimate by centroid
    d = 50
    X, Y = np.arange(x - d, x + d), np.arange(y - d, y + d)
    V = Im[X, Y]
    D = sum(V)
    x = int(sum(V * X) / D)
    y = int(sum(V * Y) / D)

    # use new center for hfr
    X, Y = np.arange(x - d, x + d), np.arange(y - d, y + d)
    V = Im[X, Y]

    D = np.array(np.vstack((X - x, Y - y)))
    D = np.linalg.norm(D, axis=0)
    hfr = np.sum(V * D) / np.sum(V)
    return hfr


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
