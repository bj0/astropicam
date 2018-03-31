import os

import click
from kivy import resources
from kivy.config import Config

import picam.config as cfg
from picam.camapp import CamApp

try:
    import picamera

    _has_cam = True
except ImportError:
    _has_cam = False

cfg.FAKE = not _has_cam


@click.command()
@click.option('--fake', default=cfg.FAKE, help='force FAKE mode')
def main(fake):
    # make sure we stash forced value
    cfg.FAKE = fake

    # but if we don't have picamera, we have to fake it anyway
    if not cfg.FAKE and not _has_cam:
        cfg.FAKE = True

    if not cfg.FAKE:
        Config.set("graphics", 'show_cursor', 0)

    Config.set('graphics', 'width', '320')
    Config.set('graphics', 'height', '240')

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

    # launch app
    if cfg.FAKE:
        CamApp(None).run()
    else:
        with picamera.PiCamera(sensor_mode=cfg.MODE, framerate=cfg.FRAME_RATE) as camera:
            CamApp(camera).run()
