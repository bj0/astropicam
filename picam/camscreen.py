import time
from enum import Enum

from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, ConfigParserProperty
from kivy.uix.screenmanager import Screen

import picam.config as cfg
from picam.fake import FakeSource
from picam.maths import measure_hfr, measure_lp
from picam.utils import threaded, set_camera_mode, print_sensor
from .textureoutput import TextureOutput


class MeasureType(Enum):
    HFR = 'HFR'
    LP = 'LP'

    def __str__(self):
        return self.value


# noinspection PyArgumentList
class CamScreen(Screen):
    tex = ObjectProperty(None)
    recording = BooleanProperty(False)
    playing = BooleanProperty(False)
    measure_type = ConfigParserProperty(None, 'view', 'focus', 'app', val_type=MeasureType)
    measure_frequency = ConfigParserProperty(5, 'view', 'focus_rate', 'app', val_type=int)
    measure = False
    zoom_factor = NumericProperty(1)  # todo more options (set in cfg?)

    iso = ConfigParserProperty(None, 'camera', 'iso', 'app', val_type=int,
                               verify=lambda x: 100 <= x <= 800, errorvalue=800)
    framerate = ConfigParserProperty(None, 'camera', 'framerate', 'app', val_type=int,
                                     verify=lambda x: 1 <= x <= 90, errvalue=10)
    exposure_mode = ConfigParserProperty(None, 'camera', 'exposure_mode', 'app')
    sensor_mode = ConfigParserProperty(None, 'camera', 'sensor_mode', 'app')

    _measure_tick = 0

    _fake_source = FakeSource()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.texout = TextureOutput()
        self.tex = self.texout.texture

    def on_new_measure(self, fm):
        print(self.measure_type, fm)
        pass

    # noinspection PyAttributeOutsideInit
    def init(self, camera):
        self.register_event_type('on_new_measure')

        self.cam = camera
        self.texout.bind(on_update=self._texture_update)

        # todo set mode/framerate?

    def on_iso(self, _, value):
        print('iso', value)
        if not cfg.FAKE:
            self.cam.iso = value

    def on_framerate(self, _, value):
        print('framerate', value)
        if not cfg.FAKE:
            set_camera_mode(self.cam, self.exposure_mode, framerate=value)

    def on_sensor_mode(self, _, value):
        print('mode', value)
        if not cfg.FAKE:
            set_camera_mode(self.cam, self.exposure_mode, mode=value)

    def on_exposure_mode(self, _, value):
        print('exposure_mode', value)
        if not cfg.FAKE:
            self.cam.exposure_mode = value

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
                print_sensor(cam)
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
        if cfg.FAKE:
            self._fake_source.zoom()
        else:
            zf = self.zoom_factor + 1
            self.zoom_factor = zf if zf <= 3 else 1

            scale = 1.0 if self.zoom_factor == 1 else 1.0 / self.zoom_factor
            offset = 0.0 if self.zoom_factor == 1 else (1.0 - scale) / 2.0
            print('new zoom:', self.zoom_factor, scale, offset)
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
                    fm = measure_lp(buf)
                else:
                    fm = 0
                # fm = measure_fwhm(buf)
                self.dispatch('on_new_measure', fm)


if __name__ == '__main__':
    from timeit import default_timer as timer

    with open('3/frame-560.932599', 'rb') as f:
        buf = f.read()

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
        measure_lp(buf)
    end = timer()
    print(f'focus time: {(end-start)/N}')
