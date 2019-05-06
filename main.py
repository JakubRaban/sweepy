from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from game import Game


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
    def __init__(self, board_height, board_width, players, **kwargs):
        super(SweepyGame, self).__init__(**kwargs)
        self.cols = board_width
        self.rows = board_height
        self.spacing = [2, 2]
        global game
        game = Game(board_height, board_width, players)
        self.all_tiles = dict()
        Window.size = 32 * self.cols - 2, 32 * self.rows - 2
        for i in range(self.rows):
            for j in range(self.cols):
                self.all_tiles[(i, j)] = Image(source='images/tile.png', width=30, height=30, size_hint_x=None, size_hint_y=None)
                self.add_widget(self.all_tiles.get((i, j)))
        self.update_cell(0, 0)
        self.update_cell(board_height - 1, 0)
        self.update_cell(0, board_width - 1)
        self.update_cell(board_height - 1, board_width - 1)

    def update_cell(self, row, column):
        filename = "images/tile"
        our_cell = game.board.get_cell_by_indexes(row, column)
        if our_cell.is_uncovered:
            if our_cell.has_mine:
                filename += "_mine"
            else:
                filename += ("_" + str(our_cell.mines_around))
        if not our_cell.has_mine:
            if our_cell.flagging_player is not None:
                filename += "_flag"
                if our_cell.has_mine:
                    filename += "_ok"
                else:
                    filename += "_bad"
            for player in game.players:
                if player.get_position() == (row, column):
                    filename += ("_player_" + player.color.value)
        filename += ".png"
        self.all_tiles[(row, column)].source = filename


class SweepyApp(App):
    def build(self):
        return SweepyGame(25, 25, 4)


if __name__ == '__main__':
    SweepyApp().run()
