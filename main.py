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


class WholeWindow(BoxLayout):
    def __init__(self, board_height, board_width, players, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        grid = GridLayout(height=50, size_hint_y=None)
        grid.rows = 2
        grid.cols = 2
        score_player_red = Label(text='0', bold=True, color=[203/256, 30/256, 30/256, 0])
        grid.add_widget(Label(text='0'))
        grid.add_widget(score_player_red)
        grid.add_widget(Label(text='0'))
        grid.add_widget(Label(text='0'))
        self.add_widget(grid)
        self.add_widget(SweepyGame(board_height, board_width, players))

    def update_labels(self):
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
        Window.size = 27 * self.cols - 2, 27 * self.rows - 2 + 50
        for i in range(self.rows):
            for j in range(self.cols):
                self.all_tiles[(i, j)] = Image(source='images/tile.png', width=25, height=25, size_hint_x=None, size_hint_y=None)
                self.add_widget(self.all_tiles.get((i, j)))
        self.update_cell(0, 0)
        self.update_cell(board_height - 1, 0)
        self.update_cell(0, board_width - 1)
        self.update_cell(board_height - 1, board_width - 1)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text'
        )
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def update_cell(self, row, column):
        filename = "images/tile"
        our_cell = game.board.get_cell_by_indexes(row, column)
        if our_cell.is_uncovered:
            if our_cell.has_mine:
                filename += "_mine"
            else:
                filename += ("_" + str(our_cell.mines_around))
        if filename.find("mine") == -1:
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

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        moved = True
        if keycode[1] == 'left':
            game.move_player(0, MoveDirection.LEFT)
        elif keycode[1] == 'right':
            game.move_player(0, MoveDirection.RIGHT)
        elif keycode[1] == 'down':
            game.move_player(0, MoveDirection.DOWN)
        elif keycode[1] == 'up':
            game.move_player(0, MoveDirection.UP)
        elif keycode[1] == ',':
            game.uncover_cell(0)
            moved = False
        elif keycode[1] == '.':
            game.flag_cell(0)

        if keycode[1] == 'a':
            game.move_player(1, MoveDirection.LEFT)
        elif keycode[1] == 'd':
            game.move_player(1, MoveDirection.RIGHT)
        elif keycode[1] == 's':
            game.move_player(1, MoveDirection.DOWN)
        elif keycode[1] == 'w':
            game.move_player(1, MoveDirection.UP)
        elif keycode[1] == 'f':
            game.uncover_cell(1)
            moved = False
        elif keycode[1] == 'g':
            game.flag_cell(1)

        if moved:
            pass
        for i in range(self.rows):
            for j in range(self.cols):
                self.update_cell(i, j)

        if keycode[1] == 'escape':
            keyboard.release()
        return True


class SweepyApp(App):
    def build(self):
        return WholeWindow(30, 35, 2)


if __name__ == '__main__':
    SweepyApp().run()
