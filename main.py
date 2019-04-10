from kivy.app import App
from kivy.clock import Clock
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
        self.spacing = [2,2]
        self.all_tiles = dict()
        Window.size = 32 * self.cols, 32 * self.rows
        for i in range(self.cols):
            for j in range(self.rows):
                self.all_tiles[(i, j)] = Image(source='images/tile_normal.png', width=30, height=30, size_hint_x=None, size_hint_y=None)
                self.add_widget(self.all_tiles[(i, j)])
        self.all_tiles[(3, 6)].source = 'images/tile_flagged_ok.png'
        self.all_tiles[(3, 6)].reload()
        self.all_tiles[(3, 7)].source = 'images/tile_two.png'
        self.all_tiles[(3, 7)].reload()


class SweepyApp(App):
    def build(self):
        return SweepyGame(10, 10)


if __name__ == '__main__':
    SweepyApp().run()
