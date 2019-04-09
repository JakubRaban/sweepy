from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition


class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)


class SummaryScreen(Screen):
    pass


class GameScreen(Screen):
    pass


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(GameScreen(name='game'))
sm.add_widget(SummaryScreen(name='summary'))
sm.transition = NoTransition()


class SweepyGame(GridLayout):
    def __init__(self, board_width, board_height, **kwargs):
        super(SweepyGame, self).__init__(**kwargs)
        self.cols = board_width
        self.rows = board_height
        self.spacing = [1, 1]
        Window.size = 31 * self.cols, 31 * self.rows
        for i in range(self.cols):
            for j in range(self.rows):
                self.add_widget(Image(source='images/tile_normal.png', width=30, height=30, size_hint_x=None, size_hint_y=None))


class SweepyApp(App):
    def build(self):
        return SweepyGame(35, 25)


if __name__ == '__main__':
    SweepyApp().run()
