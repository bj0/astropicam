# want:
# * enabling zooming (with sensor, not software)
# * capture cropped sensor to eliminate scaling? or just do binning?
# * add recording, what settings?
# * add full image capture?
# * calf fwhm?
# * add temperature
# * add saving frames?
import os

from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '240')

import picam.config as cfg
from picam.camapp import CamApp

try:
    import picamera

    cfg.FAKE = False
except ImportError:
    cfg.FAKE = True

from kivy import resources

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

if __name__ == '__main__':
    if cfg.FAKE:
        CamApp(None).run()
    else:
        with picamera.PiCamera(sensor_mode=4, framerate=cfg.FRAME_RATE) as camera:
            CamApp(camera).run()
