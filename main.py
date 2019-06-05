import os

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.widget import Widget

from board import MoveDirection
from game import Game, Perk

kv = Builder.load_file("layout.kv")


def get_screen_size():
    screen_info = os.popen("xrandr -q -d :0").readlines()[0]
    screen_info_split = screen_info.split()
    return int(screen_info_split[7]), int(screen_info_split[9][:-1])


class MenuScreen(Screen):
    def play_btn(self, if_single):
        sm.switch_to(ParametersScreen(if_single))


class ParametersScreen(Screen):

    nb_of_players = 1

    def __init__(self, if_single, **kwargs):
        super().__init__(**kwargs)
        self.blue_player.disabled = if_single
        self.red_player.disabled = if_single
        self.green_player.disabled = if_single
        self.yellow_player.disabled = if_single

    def play_btn(self):
        try:
            max_value = max(int(self.board_width.text), int(self.board_height.text))
            min_value = min(int(self.board_width.text), int(self.board_height.text))
            if min_value >= 5 and max_value <= 30:
                sm.switch_to(GameScreen(name="game", board_height=int(self.board_height.text),
                                        board_width=int(self.board_width.text),
                                        players=self.nb_of_players))
            else:
                self.invalid_form()
        except ValueError:
            self.not_a_number_form()

    def invalid_form(self):
        pop = Popup(title='Invalid board size values!',
                    content=Label(text='Please type board dimensions with values between 5 and 30.'),
                    size_hint=(None, None), size=(600, 100))
        pop.open()

    def not_a_number_form(self):
        pop = Popup(title='Invalid board size values!',
                    content=Label(text='Please give integers!'),
                    size_hint=(None, None), size=(600, 100))
        pop.open()

    def add_players(self, id):
        self.nb_of_players = id
        self.blue_player.state = 'down' if id > 0 else 'normal'
        self.red_player.state = 'down' if id > 1 else 'normal'
        self.green_player.state = 'down' if id > 2 else 'normal'
        self.yellow_player.state = 'down' if id > 3 else 'normal'

    def reset(self):
        self.board_width.text = ""
        self.board_height.text = ""


class GameScreen(Screen):
    def __init__(self, board_height, board_width, players, **kwargs):
        super().__init__(**kwargs)
        self.box_arrangement = WholeWindow(board_height, board_width, players)
        self.box_arrangement.parent_window = self
        self.add_widget(self.box_arrangement)
        self.game_result = None

    def finish(self, result):
        Window.size = (800, 800)
        sm.switch_to(SummaryScreen(result))


class SummaryScreen(Screen):
    def __init__(self, game_result, **kwargs):
        super().__init__(**kwargs)
        self.blue_player_score.text += game_result[0][0].text
        self.red_player_score.text += game_result[0][1].text
        self.green_player_score.text += game_result[0][2].text
        self.yellow_player_score.text += game_result[0][3].text

        if game_result[1].all_players_dead():
            self.game_over.text = "All players are dead!"
        elif game_result[1].board.remaining_mines == 0:
            self.game_over.text = "The area is clear!"
        else:
            self.game_over.text = "Game finished"

    def play_btn(self):
        sm.switch_to(MenuScreen(name="menu"))


class ScoreLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 24
        self.bold = True
        self.text = '0'
        self.size_hint_x = 0.2


class PerkImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'images/tile.png'
        self.size_hint_x = 0.2


class WholeWindow(BoxLayout):
    def __init__(self, board_height, board_width, players, **kwargs):
        super().__init__(**kwargs)
        self.game = Game(board_height, board_width, players)
        self.game.window = self

        self.end = Label(text='Koniec', color=[0, 0, 0, 0])
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
        self.score_table.add_widget(Button(text="Finish the game", background_normal='', background_color=[0, 0, 0, 0],
                                           on_press=self.endgame_button_press))
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

    def endgame_button_press(self, _):
        self.parent.finish((self.score_labels, self.game))

    def update_labels(self):
        for index in range(len(self.game.players)):
            self.score_labels[index].text = str(self.game.players[index].score)
            filename = 'images/tile'
            if self.game.players[index].is_dead:
                filename += "_mine"
            elif self.game.players[index].perk:
                filename += ("_perk_" + self.game.players[index].perk.name.value)
            filename += ".png"
            self.perk_indicators[index].source = filename
        self.number_of_mines.text = self.get_remaining_mines_text()
        if self.game.is_finished():
            self.end.color = [1, 0, 0, 0]
            final_result = self.score_labels, self.game
            Clock.schedule_once(lambda dt: self.parent.finish(final_result), 2)

    def get_remaining_mines_text(self):
        return "Mines remaining: " + str(self.game.board.remaining_mines) \
               + "/" + str(self.game.board.total_number_of_mines)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        try:
            before_position = [player.get_position() for player in self.game.players]

            uncovered = []
            if keycode[1] == 'left':
                self.game.move_player(0, MoveDirection.LEFT)
            elif keycode[1] == 'right':
                self.game.move_player(0, MoveDirection.RIGHT)
            elif keycode[1] == 'down':
                self.game.move_player(0, MoveDirection.DOWN)
            elif keycode[1] == 'up':
                self.game.move_player(0, MoveDirection.UP)
            elif keycode[1] == ',':
                uncovered = self.game.uncover_cell(0)
            elif keycode[1] == '.':
                self.game.flag_cell(0)
            elif keycode[1] == '/':
                uncovered = self.game.drop_item(0)

            if keycode[1] == 'a':
                self.game.move_player(1, MoveDirection.LEFT)
            elif keycode[1] == 'd':
                self.game.move_player(1, MoveDirection.RIGHT)
            elif keycode[1] == 's':
                self.game.move_player(1, MoveDirection.DOWN)
            elif keycode[1] == 'w':
                self.game.move_player(1, MoveDirection.UP)
            elif keycode[1] == 'f':
                uncovered = self.game.uncover_cell(1)
            elif keycode[1] == 'g':
                self.game.flag_cell(1)
            elif keycode[1] == 'v':
                uncovered = self.game.drop_item(1)

            if keycode[1] == 'numpad4':
                self.game.move_player(2, MoveDirection.LEFT)
            elif keycode[1] == 'numpad6':
                self.game.move_player(2, MoveDirection.RIGHT)
            elif keycode[1] == 'numpad5':
                self.game.move_player(2, MoveDirection.DOWN)
            elif keycode[1] == 'numpad8':
                self.game.move_player(2, MoveDirection.UP)
            elif keycode[1] == 'numpaddivide':
                uncovered = self.game.uncover_cell(2)
            elif keycode[1] == 'numpadmul':
                self.game.flag_cell(2)
            elif keycode[1] == 'numpadsubstract':
                uncovered = self.game.drop_item(2)

            if keycode[1] == 'j':
                self.game.move_player(3, MoveDirection.LEFT)
            elif keycode[1] == 'l':
                self.game.move_player(3, MoveDirection.RIGHT)
            elif keycode[1] == 'k':
                self.game.move_player(3, MoveDirection.DOWN)
            elif keycode[1] == 'i':
                self.game.move_player(3, MoveDirection.UP)
            elif keycode[1] == '[':
                uncovered = self.game.uncover_cell(3)
            elif keycode[1] == ']':
                self.game.flag_cell(3)
            elif keycode[1] == '\\':
                uncovered = self.game.drop_item(3)

            after_position = [player.get_position() for player in self.game.players]

            cells_to_update = before_position + uncovered + after_position

            for cell in cells_to_update:
                self.game_grid.update_cell(cell[0], cell[1], self.game)

            self.update_labels()
        except IndexError:
            pass

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
        if our_cell.perk:
            filename += ("_perk_" + our_cell.perk.name.value)
        if our_cell.is_uncovered:
            if our_cell.has_mine:
                filename += "_mine"
            else:
                filename += ("_" + str(our_cell.mines_around))
        if "mine" not in filename:
            if our_cell.flagging_player and not our_cell.is_uncovered:
                filename += "_flag"
                if our_cell.has_mine:
                    filename += "_ok"
                    if not our_cell.has_mine_from_start:
                        filename += "_caution"
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


sm = ScreenManager()
sm.add_widget(MenuScreen(name="menu"))
sm.transition = NoTransition()

sm.current = "menu"


class SweepyApp(App):
    def build(self):
        return sm
        #return TestJoystick()


if __name__ == '__main__':
    SweepyApp().run()
