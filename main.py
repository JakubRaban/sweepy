from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from board import MoveDirection
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


class WholeWindow(BoxLayout):
    def __init__(self, board_height, board_width, players, **kwargs):
        super().__init__(**kwargs)
        self.game = Game(board_height, board_width, players)

        score_player_blue = Label(text='0', bold=True, color=[63 / 255, 115 / 255, 232 / 255, 0])
        score_player_red = Label(text='0', bold=True, color=[203 / 255, 30 / 255, 30 / 255, 0])
        score_player_green = Label(text='0', bold=True, color=[53 / 255, 219 / 255, 35 / 255, 0])
        score_player_yellow = Label(text='0', bold=True, color=[255 / 255, 186 / 255, 0, 0])
        self.score_labels = [score_player_blue, score_player_red, score_player_green, score_player_yellow]
        permutation_matrix = [2, 1, 0, 3]
        self.score_labels = self.score_labels[0:players-1]

        self.orientation = 'vertical'
        self.score_table = GridLayout(height=50, size_hint_y=None, rows=2, cols=2)
        self.score_table.add_widget(score_player_green)
        self.score_table.add_widget(score_player_red)
        self.score_table.add_widget(score_player_blue)
        self.score_table.add_widget(score_player_yellow)
        self.add_widget(self.score_table)
        self.game_grid = GameBoard(board_height, board_width, players)
        self.add_widget(self.game_grid)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text'
        )
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def update_labels(self):
        for index, label in enumerate(self.score_labels):
            label.text = str(self.game.players[index].score)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.game.move_player(0, MoveDirection.LEFT)
        elif keycode[1] == 'right':
            self.game.move_player(0, MoveDirection.RIGHT)
        elif keycode[1] == 'down':
            self.game.move_player(0, MoveDirection.DOWN)
        elif keycode[1] == 'up':
            self.game.move_player(0, MoveDirection.UP)
        elif keycode[1] == ',':
            self.game.uncover_cell(0)
        elif keycode[1] == '.':
            self.game.flag_cell(0)

        if keycode[1] == 'a':
            self.game.move_player(1, MoveDirection.LEFT)
        elif keycode[1] == 'd':
            self.game.move_player(1, MoveDirection.RIGHT)
        elif keycode[1] == 's':
            self.game.move_player(1, MoveDirection.DOWN)
        elif keycode[1] == 'w':
            self.game.move_player(1, MoveDirection.UP)
        elif keycode[1] == 'f':
            self.game.uncover_cell(1)
        elif keycode[1] == 'g':
            self.game.flag_cell(1)

        if keycode[1] in ['.', 'g']:
            self.update_labels()

        for i in range(self.game_grid.rows):
            for j in range(self.game_grid.cols):
                self.game_grid.update_cell(i, j, self.game)

        if keycode[1] == 'escape':
            keyboard.release()
        return True


class GameBoard(GridLayout):
    def __init__(self, board_height, board_width, players, **kwargs):
        super(GameBoard, self).__init__(**kwargs)
        self.cols = board_width
        self.rows = board_height
        self.spacing = [2, 2]
        self.all_tiles = dict()
        Window.size = 27 * self.cols - 2, 27 * self.rows - 2 + 50
        for i in range(self.rows):
            for j in range(self.cols):
                self.all_tiles[(i, j)] = Image(source='images/tile.png', width=25, height=25, size_hint_x=None, size_hint_y=None)
                self.add_widget(self.all_tiles.get((i, j)))
        self.all_tiles[(board_height - 1, 0)].source = 'images/tile_player_blue.png'
        if players >= 2:
            self.all_tiles[(0, board_width - 1)].source = 'images/tile_player_red.png'
        if players >= 3:
            self.all_tiles[(0, 0)].source = 'images/tile_player_green.png'
        if players >= 4:
            self.all_tiles[(board_height - 1, board_width - 1)].source = 'images/tile_player_yellow.png'

    def update_cell(self, row, column, game):
        filename = "images/tile"
        our_cell = game.board.get_cell_by_indexes(row, column)
        if our_cell.is_uncovered:
            if our_cell.has_mine:
                filename += "_mine"
            else:
                filename += ("_" + str(our_cell.mines_around))
        if filename.find("mine") == -1:
            if our_cell.flagging_player is not None and not our_cell.is_uncovered:
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
        return WholeWindow(20, 25, 2)


if __name__ == '__main__':
    SweepyApp().run()
