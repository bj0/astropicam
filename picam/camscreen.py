import time
from enum import Enum
from math import sqrt

import cv2
import numpy as np
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen
from photutils import find_peaks
from photutils.centroids import fit_2dgaussian

import picam.config as cfg
from picam.fake import FakeSource
from picam.utils import threaded
from .textureoutput import TextureOutput


class MeasureType(Enum):
    HFR = 1
    LP = 2


class CamScreen(Screen):
    tex = ObjectProperty(None)
    recording = BooleanProperty(False)
    playing = BooleanProperty(False)
    measure_type = ObjectProperty(MeasureType.HFR, rebind=True)
    measure_frequency = NumericProperty(cfg.MEASURE_RATE)
    measure = False
    zoom_factor = NumericProperty(1)  # todo more options (set in cfg?)

    _measure_tick = 0

    _fake_source = FakeSource()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.texout = TextureOutput()
        self.tex = self.texout.texture

    def on_new_measure(self, fm):
        pass

    def init(self, camera):
        self.register_event_type('on_new_measure')

        self.cam = camera
        self.texout.bind(on_update=self._texture_update)

    def play(self):
        print('play')
        self.playing = not self.playing
        if self.playing:
            if cfg.FAKE:
                print('fake play')

                @threaded(daemon=True)
                def run_fake_source():
                    print('start fake playing')
                    for buf in self._fake_source:
                        if not self.playing:
                            break
                        self.texout.write(buf)
                        time.sleep(1 / float(cfg.FRAME_RATE))
                    print('done fake playing')

                run_fake_source()
            else:
                self.cam.start_recording(self.texout, 'rgb', resize=(320, 240))
        else:
            if cfg.FAKE:
                print('fake stop')
            else:
                self.cam.stop_recording()

    def capture(self):
        print('capture')
        if not cfg.FAKE:
            self.cam.capture('image-{}.jpg'.format(time.clock()), resize=(3280, 2464))

    def record(self):
        print('record')
        self.recording = not self.recording
        if not cfg.FAKE:
            if self.recording:
                self.cam.start_recording('video-{}.h264'.format(time.clock()),
                                         splitter_port=2, resize=(1640, 1232))
            else:
                self.cam.stop_recording(splitter_port=2)

    def zoom(self):  # todo make zoom switch source directories in fake mode?
        zf = self.zoom_factor + 1
        self.zoom_factor = zf if zf <= 3 else 1

        scale = 1.0 if self.zoom_factor == 1 else 1.0 / self.zoom_factor
        offset = 0.0 if self.zoom_factor == 1 else (1.0 - scale) / 2.0
        print('new zoom:', self.zoom_factor, scale, offset)
        if not cfg.FAKE:
            self.cam.zoom = (offset, offset, scale, scale)

    def _texture_update(self, _, buf):
        # self.canvas.ask_update()
        if self.measure:
            self._measure_tick -= 1
            if self._measure_tick <= 0:
                self._measure_tick = self.measure_frequency
                if self.measure_type is MeasureType.HFR:
                    fm = measure_hfr(buf)
                elif self.measure_type is MeasureType.LP:
                    fm = measure_focus(buf)
                else:
                    fm = 0
                # fm = measure_fwhm(buf)
                self.dispatch('on_new_measure', fm)


def measure_focus(buf):
    im = np.frombuffer(buf, dtype=np.uint8).reshape((240, 320, 3))
    im = np.roll(im, 1, axis=-1)
    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def measure_fwhm(buf):
    im = np.frombuffer(buf, dtype=np.uint8).reshape((240, 320, 3))
    fit = fit_2dgaussian(im[:, :, 1])
    # print(fit)
    f = sqrt(fit.x_stddev ** 2 + fit.y_stddev ** 2) * 2.3548200450309493
    # print('f=', f)
    return f


def measure_hfr(buf):
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


if __name__ == '__main__':
    from timeit import default_timer as timer

    with open('3/frame-560.932599', 'rb') as f:
        buf = f.read()

    # measure_hfr(buf)
    # exit(0)

    # N = 10
    # start = timer()
    # for i in range(N):
    #     measure_fwhm(buf)
    # end = timer()
    # print(f'fwhm time: {(end-start)/N}')

    N = 10
    start = timer()
    for i in range(N):
        measure_hfr(buf)
    end = timer()
    print(f'hfr time: {(end-start)/N}')

    N = 10
    start = timer()
    for i in range(N):
        measure_focus(buf)
    end = timer()
    print(f'focus time: {(end-start)/N}')
