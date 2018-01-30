# want:
# * enabling zooming (with sensor, not software)
# * capture cropped sensor to eliminate scaling? or just do binning?
# * add recording, what settings?
# * add full image capture?
# * calf fwhm?
# * add temperature
import os
import time
from collections import deque

import cv2
import numpy as np
from kivy.event import EventDispatcher
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen

try:
    import picamera

    _fake = False
except ImportError:
    _fake = True

from kivy.app import App
from kivy.clock import mainthread, Clock
# from kivy.core.camera import Camera
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, StringProperty
from kivy import resources

from .utils import measure_temp
from .plotscreen import PlotScreen

# this is needed so kv files can find images
resources.resource_add_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'res'
    ))
# and this one is for loading kv files
resources.resource_add_path(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'kv'
    ))


class TextureOutput(EventDispatcher):
    def __init__(self):
        super(TextureOutput, self).__init__()
        self.register_event_type('on_update')
        self.texture = Texture.create(size=(320, 240))

    @mainthread
    def write(self, buf):
        self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.dispatch('on_update', buf)
        # self.root.canvas.ask_update()

    def on_update(self, buf):
        pass


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
            if _fake:
                print('fake record')
                self.tex = Image(source='m45_filter.png').texture
            else:
                self.cam.start_recording(self.texout, 'rgb', resize=(320, 240))
        else:
            if _fake:
                print('fake stop')
            else:
                self.cam.stop_recording()

    def capture(self):
        print('capture')
        if not _fake:
            self.cam.capture('image-{}.jpg'.format(time.clock()), resize=(3280, 2464))

    def record(self):
        print('record')
        self.recording = not self.recording
        if not _fake:
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
        if not _fake:
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


class CamApp(App):
    tex = ObjectProperty(None)
    alpha = NumericProperty(0.90)
    current = StringProperty("0")
    temperature = StringProperty('0°')
    values = deque([0] * 100)

    def __init__(self, camera):
        super(CamApp, self).__init__()
        self.cam = camera

    def build(self):
        root = Builder.load_file('camapp.kv')
        root.ids.cam.init(self.cam)
        self.tex = root.ids.cam.tex
        root.ids.cam.bind(tex=self.setter('tex'))  # ugly workaround
        root.ids.cam.texout.bind(on_update=lambda *x: root.canvas.ask_update())

        root.ids.plot_screen.init()

        root.ids.cam.bind(on_new_measure=self.update_measure)

        self.cam_screen = root.ids.cam
        self.plot_screen = root.ids.plot_screen

        Clock.schedule_interval(self.update_temperature, 3)

        return root

    def update_measure(self, _, fm):
        fme = self.values[-1] * self.alpha + (1 - self.alpha) * fm

        self.values.popleft()
        self.values.append(fme)

        # print('new measure: {}'.format(fme))
        self.plot_screen.update_plot(self.values)
        self.current = "{}".format(int(fme))

    def update_temperature(self, _):
        self.temperature = '{:.1f}°'.format(measure_temp())


if __name__ == '__main__':
    if _fake:
        CamApp(None).run()
    else:
        with picamera.PiCamera(sensor_mode=4) as camera:
            CamApp(camera).run()
