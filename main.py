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
        self.spacing = [2,2]
        self.all_tiles = dict()
        Window.size = 32 * self.cols - 2, 32 * self.rows - 2
        for i in range(self.rows):
            for j in range(self.cols):
                self.all_tiles[(i, j)] = Image(source='images/tile_normal.png', width=30, height=30, size_hint_x=None, size_hint_y=None)
                self.add_widget(self.all_tiles.get((i, j)))
        self.all_tiles[(2, 4)].source = 'images/tile_flagged_ok.png'
        self.all_tiles[(0, 2)].source = 'images/tile_two.png'
        self.all_tiles[(5, 7)].source = 'images/tile_zero.png'


class SweepyApp(App):
    def build(self):
        return SweepyGame(35, 25)


if __name__ == '__main__':
    SweepyApp().run()
