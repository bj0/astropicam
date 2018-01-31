from kivy.clock import mainthread
from kivy.event import EventDispatcher
from kivy.graphics.texture import Texture


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
