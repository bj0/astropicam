# -*- coding: utf-8 -*-

from kivy import resources
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, Clock

from picam.utils import measure_temp


class CamApp(App):
    """
    Main App Class
    """

    tex = ObjectProperty(None)
    temperature = StringProperty('0°')

    # save_frames = BooleanProperty(False)

    def __init__(self, camera):
        super(CamApp, self).__init__()
        self.cam = camera

        # settings are in app path
        resources.resource_add_path(self.directory)

    def build_config(self, config):
        config.setdefaults('view', {
            'stretch': 'SQRT',
            'focus': 'HFR',
            'focus_rate': 5
        })
        config.setdefaults('camera', {
            'exposure_mode': 'off',
            'framerate': 10,
            'iso': 800,
            'sensor_mode': 4
        })

    def build_settings(self, settings):
        settings.add_json_panel('picam', self.config, resources.resource_find('settings.json'))

    # noinspection PyAttributeOutsideInit
    def build(self):

        self.title = "RPi Astro Cam"

        # load root
        root = Builder.load_file('camapp.kv')
        cam_screen = root.ids.cam
        plot_screen = root.ids.plot_screen

        # CamScreen needs the camera object, and we need it's texture
        cam_screen.init(self.cam)
        self.tex = cam_screen.tex
        cam_screen.bind(tex=self.setter('tex'))  # ugly workaround
        # redraw on texture change
        cam_screen.texout.bind(on_update=lambda *x: root.canvas.ask_update())

        # create plot
        plot_screen.init()

        cam_screen.bind(on_new_measure=plot_screen.update_measure)

        Clock.schedule_interval(self.update_temperature, 3)

        return root

    def update_temperature(self, _):
        self.temperature = '{:.1f}°'.format(measure_temp())
