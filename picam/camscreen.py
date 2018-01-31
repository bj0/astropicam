import time

import cv2
import picam.config as cfg
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen

from .textureoutput import TextureOutput


class CamScreen(Screen):
    tex = ObjectProperty(None)
    recording = BooleanProperty(False)
    playing = BooleanProperty(False)
    measure_frequency = NumericProperty(5)
    measure = False
    zoom_factor = 1

    _tick = 0

    def on_new_measure(self, fm):
        pass

    def init(self, camera):
        self.register_event_type('on_new_measure')

        self.texout = TextureOutput()
        self.cam = camera
        self.tex = self.texout.texture
        self.texout.bind(on_update=self._texture_update)

    def play(self):
        print('play')
        self.playing = not self.playing
        if self.playing:
            if cfg.FAKE:
                print('fake record')
                self.tex = Image(source='m45_filter.png').texture
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

    def zoom(self):
        self.zoom_factor += 1
        if self.zoom_factor > 3:
            self.zoom_factor = 1
        scale = 1.0 if self.zoom_factor == 1 else 1.0 / self.zoom_factor
        offset = 0.0 if self.zoom_factor == 1 else (1.0 - scale) / 2.0
        print('new zoom:', self.zoom_factor, scale, offset)
        if not cfg.FAKE:
            self.cam.zoom = (offset, offset, scale, scale)

    def _texture_update(self, _, buf):
        # self.canvas.ask_update()
        if self.measure:
            self._tick -= 1
            if self._tick <= 0:
                self._tick = self.measure_frequency
                im = np.frombuffer(buf, dtype=np.uint8).reshape((240, 320, 3))
                im = np.roll(im, 1, axis=-1)
                gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
                fm = cv2.Laplacian(gray, cv2.CV_64F).var()

                self.dispatch('on_new_measure', fm)

