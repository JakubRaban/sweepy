
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.widget import Widget

from board import MoveDirection
from game import Game, Perk
import os


def get_screen_size():
    screen_info = os.popen("xrandr -q -d :0").readlines()[0]
    screen_info_split = screen_info.split()
    return int(screen_info_split[7]), int(screen_info_split[9][:-1])


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


class ScoreLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 24
        self.bold = True
        self.text = '0'
        self.size_hint_x = 0.1


class PerkImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'images/tile.png'
        self.size_hint_x = 0.1


class WholeWindow(BoxLayout):
    def __init__(self, board_height, board_width, players, **kwargs):
        super().__init__(**kwargs)
        self.game = Game(board_height, board_width, players)
        self.game.window = self

        self.end = Label(text='Koniec', color=[0,0,0,0])
        self.number_of_mines = Label(text=self.get_remaining_mines_text())
        score_player_blue = ScoreLabel(color=[63 / 255, 115 / 255, 232 / 255, 0])
        score_player_red = ScoreLabel(color=[203 / 255, 30 / 255, 30 / 255, 0])
        score_player_green = ScoreLabel(color=[53 / 255, 219 / 255, 35 / 255, 0])
        score_player_yellow = ScoreLabel(color=[255 / 255, 186 / 255, 0, 0])
        self.score_labels = [score_player_blue, score_player_red, score_player_green, score_player_yellow]
        perk_player_blue = PerkImage()
        perk_player_red = PerkImage()
        perk_player_green = PerkImage()
        perk_player_yellow = PerkImage()
        self.perk_indicators = [perk_player_blue, perk_player_red, perk_player_green, perk_player_yellow]

        for i in range(4)[players:4]:
            self.score_labels[i].color = [0, 0, 0, 0]

        self.orientation = 'vertical'
        scoreboard_height = 70
        tile_spacing = 2
        self.score_table = GridLayout(height=scoreboard_height, size_hint_y=None, rows=2, cols=5, spacing=[2, 2])
        self.score_table.add_widget(score_player_green)
        self.score_table.add_widget(perk_player_green)
        self.score_table.add_widget(Button(text="Zakończ grę", background_normal='', background_color=[0, 0, 0, 0]))
        self.score_table.add_widget(perk_player_red)
        self.score_table.add_widget(score_player_red)
        self.score_table.add_widget(score_player_blue)
        self.score_table.add_widget(perk_player_blue)
        self.score_table.add_widget(self.number_of_mines)
        self.score_table.add_widget(perk_player_yellow)
        self.score_table.add_widget(score_player_yellow)
        self.add_widget(self.score_table)

        screen_size = get_screen_size()
        tile_size_x = int(0.85 * min(1920, screen_size[0]) / board_width)
        tile_size_y = int(0.85 * (min(1080, screen_size[1]) - scoreboard_height) / board_height)
        tile_size = min(tile_size_x, tile_size_y)
        Window.size = (tile_size + tile_spacing) * board_width - tile_spacing, \
                      (tile_size + tile_spacing) * board_height - tile_spacing + scoreboard_height
        self.game_grid = GameBoard(board_height, board_width, tile_size, players)
        self.game_grid.spacing = [tile_spacing] * 2
        self.add_widget(self.game_grid)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text'
        )
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Config.set('graphics', 'resizable', False)

    def update_labels(self):
        for index in range(len(self.game.players)):
            self.score_labels[index].text = str(self.game.players[index].score)
            filename = 'images/tile'
            if self.game.players[index].is_dead:
                filename += "_mine"
            elif self.game.players[index].perk is not None:
                filename += ("_perk_" + self.game.players[index].perk.name.value)
            filename += ".png"
            self.perk_indicators[index].source = filename
        self.number_of_mines.text = self.get_remaining_mines_text()
        if self.game.is_finished():
            self.end.color = [1,0,0,0]

    def get_remaining_mines_text(self):
        return "Miny: " + str(self.game.board.remaining_mines) + "/" + str(self.game.board.total_number_of_mines)

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
        elif keycode[1] == '/':
            self.game.drop_item(0)

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
        elif keycode[1] == 'v':
            self.game.drop_item(1)

        if keycode[1] == 'numpad4':
            self.game.move_player(2, MoveDirection.LEFT)
        elif keycode[1] == 'numpad6':
            self.game.move_player(2, MoveDirection.RIGHT)
        elif keycode[1] == 'numpad5':
            self.game.move_player(2, MoveDirection.DOWN)
        elif keycode[1] == 'numpad8':
            self.game.move_player(2, MoveDirection.UP)
        elif keycode[1] == 'numpaddivide':
            self.game.uncover_cell(2)
        elif keycode[1] == 'numpadmul':
            self.game.flag_cell(2)
        elif keycode[1] == 'numpadsubstract':
            self.game.drop_item(2)

        if keycode[1] in ['.', 'g', ',', 'f', '/', 'v', 'numpadmul', 'numpadsubstract']:
            self.update_labels()

        for i in range(self.game_grid.rows):
            for j in range(self.game_grid.cols):
                self.game_grid.update_cell(i, j, self.game)

        if keycode[1] == 'escape':
            keyboard.release()
        return True


class GameBoard(GridLayout):
    def __init__(self, board_height, board_width, tile_size, players, **kwargs):
        super(GameBoard, self).__init__(**kwargs)
        self.cols = board_width
        self.rows = board_height
        self.all_tiles = dict()
        for i in range(self.rows):
            for j in range(self.cols):
                self.all_tiles[(i, j)] = Image(source='images/tile.png', width=tile_size,
                                               height=tile_size, size_hint_x=None, size_hint_y=None)
                self.add_widget(self.all_tiles[(i, j)])
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
        if our_cell.perk is not None:
            filename += ("_perk_" + our_cell.perk.name.value)
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
                if player.get_position() == (row, column) and not player.has_effect(Perk.Effect.INVISIBLE):
                    filename += ("_player_" + player.color.value)
        filename += ".png"
        self.all_tiles[(row, column)].source = filename


class TestJoystick(Widget):
    def __init__(self, **kwargs):
        super(TestJoystick, self).__init__(**kwargs)
        Window.bind(on_joy_button_down=self.on_joy_button_down)

    def on_joy_button_down(self, win, stickid, buttonid):
        print('button', win, stickid, buttonid)


class SweepyApp(App):
    def build(self):
        return WholeWindow(20, 25, 2)
        #return TestJoystick()


if __name__ == '__main__':
    SweepyApp().run()
