# -*- coding: utf-8 -*-
from collections import deque

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, Clock, BooleanProperty

from picam.utils import measure_temp


class CamApp(App):
    """
    Main App Class
    """
    tex = ObjectProperty(None)
    current = StringProperty("0")
    temperature = StringProperty('0°')
    values = deque([0] * 100)
    # save_frames = BooleanProperty(False)

    _P = 1.0

    def __init__(self, camera):
        super(CamApp, self).__init__()
        self.cam = camera

    def build(self):
        # load root
        root = Builder.load_file('camapp.kv')
        self.cam_screen = root.ids.cam
        self.plot_screen = root.ids.plot_screen

        # CamScreen needs the camera object, and we need it's texture
        self.cam_screen.init(self.cam)
        self.tex = self.cam_screen.tex
        self.cam_screen.bind(tex=self.setter('tex'))  # ugly workaround
        # redraw on texture change
        self.cam_screen.texout.bind(on_update=lambda *x: root.canvas.ask_update())

        # create plot
        self.plot_screen.init()

        self.cam_screen.bind(on_new_measure=self.update_measure)

        Clock.schedule_interval(self.update_temperature, 3)

        return root

    def update_measure(self, _, fm):
        # use 1-d kalman filter
        xh = self.values[-1]
        k = self._P / (self._P + 0.5)
        fme = xh + k * (fm - xh)
        self._P = (1 - k) * self._P

        self.values.popleft()
        self.values.append(fme)

        print('new measure: {}'.format(fme))
        self.plot_screen.update_plot(self.values)
        self.current = "{}".format(int(fme))

    def update_temperature(self, _):
        self.temperature = '{:.1f}°'.format(measure_temp())
