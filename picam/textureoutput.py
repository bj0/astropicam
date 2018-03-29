from enum import Enum

import numpy as np
from astropy.visualization import SqrtStretch, LinearStretch, AsinhStretch
from kivy.clock import mainthread
from kivy.event import EventDispatcher
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty, ObjectProperty


class StretchType(Enum):
    LINEAR = 1
    SQRT = 2
    # POWER = 3
    ASIN = 4


class TextureOutput(EventDispatcher):
    stretch_type = ObjectProperty(StretchType.SQRT, rebind=True)
    do_stretch = BooleanProperty(False)

    _stretch = {
        StretchType.LINEAR: LinearStretch(),
        StretchType.SQRT: SqrtStretch(),
        # StretchType.POWER: PowerStretch(),
        StretchType.ASIN: AsinhStretch()
    }

    def __init__(self):
        super(TextureOutput, self).__init__()
        self.register_event_type('on_update')
        self.texture = Texture.create(size=(320, 240))

    def write(self, buf):
        if self.do_stretch:
            buf = self.stretch(buf)
        self._blit(buf)

    @mainthread
    def _blit(self, buf):
        """
        write buffer to texture and fire event
        :param buf:
        :return:
        """
        self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.dispatch('on_update', buf)

    def on_update(self, buf):
        pass

    def stretch(self, buf):
        """
        perform the currently selected stretch method on buffer
        :param buf:
        :return:
        """
        im = np.frombuffer(buf, dtype=np.uint8)
        im = self._stretch[self.stretch_type](im / 255.0) * 255.0
        return im.astype(np.uint8).tobytes()
