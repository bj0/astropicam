from collections import deque

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, Clock

from picam.utils import measure_temp


class CamApp(App):
    """
    Main App Class
    """
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
