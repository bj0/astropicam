from kivy import Config

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ConfigParserProperty
from kivy.uix.button import Button
from kivy.uix.label import Label

Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '240')

class MyLabel(Button):
    foo = ConfigParserProperty(None, 'section', 'foo', 'app')


class MyApp(App):

    def build_config(self, config):
        config.setdefaults('section', {
            'foo': 1
        })

    def build_settings(self, settings):
        settings.add_json_panel('app', self.config, data="""
        [
         {
          "type": "options",
          "title" : "Foo",
          "desc" : "foo setting",
          "section" : "section",
          "key" : "foo",
          "options": [
          "bar", "not bar"
          ]          
         }
        ]
        """)

    def build(self):
        return Builder.load_string("""
MyLabel:
    text: 'Hello World!: '+str(self.foo)
    on_press: if True: print('hi')
""")


if __name__ == '__main__':
    MyApp().run()
