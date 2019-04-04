from kivy.app import App
from kivy.uix.widget import Widget


class SweepyGame(Widget):
    pass


class SweepyApp(App):
    def build(self):
        return SweepyGame()


if __name__ == '__main__':
    SweepyApp().run()