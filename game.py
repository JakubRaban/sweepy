from enum import Enum
from random import shuffle, uniform
from board import Board, ActionOutcome
from player import Player, PlayerColor
from kivy.clock import Clock


class Game:
    def __init__(self, rows, columns, nb_of_players):
        self.board = Board(rows, columns)
        self.players = []
        self.perk_manager = PerkManager()
        for index in range(nb_of_players):
            player = None
            if index == 0:
                player = Player(rows-1, 0, PlayerColor.BLUE)
            elif index == 1:
                player = Player(0, columns-1, PlayerColor.RED)
            elif index == 2:
                player = Player(0, 0, PlayerColor.GREEN)
            elif index == 3:
                player = Player(rows - 1, columns - 1, PlayerColor.YELLOW)
            if player is not None:
                self.players.append(player)

    def get_all_players_coords(self):
        return [(player.row, player.column) for player in self.players]

    def can_move_to(self, row, column):
        return self.board.can_move_to(row, column) and not (row, column) in self.get_all_players_coords()

    def move_player(self, player_id, move_direction):
        moving_player = self.players[player_id]
        coords = self.board.get_cell_towards(moving_player.row, moving_player.column, move_direction)
        if self.can_move_to(coords[0], coords[1]) and not self.players[player_id].is_dead:
            self.players[player_id].set_new_position(coords)
            new_perk = self.board.cells[coords].perk
            if new_perk is not None:
                self.collect_perk(new_perk, player_id)
                self.board.cells[coords].perk = None

    def uncover_cell(self, player_id):
        current_player = self.players[player_id]
        player_position = current_player.get_position()
        uncover_outcome = self.board.uncover_cell(player_position[0], player_position[1], current_player)
        if uncover_outcome == ActionOutcome.EXPLODED:
            current_player.is_dead = True

    def flag_cell(self, player_id):
        current_player = self.players[player_id]
        player_position = current_player.get_position()
        flagging_outcome = self.board.toggle_flag(player_position[0], player_position[1], current_player)
        if flagging_outcome == ActionOutcome.FLAG_CORRECT:
            current_player.add_points(1)
        elif flagging_outcome == ActionOutcome.FLAG_INCORRECT:
            current_player.add_points(-5)

    def all_players_dead(self):
        return len([player.is_dead for player in self.players if not player.is_dead]) == 0

    def is_finished(self):
        return self.board.remaining_mines == 0 or self.all_players_dead()

    def put_perk_on_board(self):
        possible_cells = self.board.get_covered_cells()
        if len(possible_cells) == 0:
            return None
        shuffle(possible_cells)
        cell_to_perk = possible_cells[0]
        cell_to_perk.perk = self.perk_manager.random_perk()
        return cell_to_perk.row, cell_to_perk.column

    def collect_perk(self, perk, player_id):
        perk.activate(player_id, self.players)
        perk_lasting_time = uniform(10, 20)
        perk.clock_event = Clock.schedule_interval(lambda dt: perk.cancel(player_id, self.players), perk_lasting_time)


class Perk:
    def __init__(self, name, effect_on_others):
        self.name = name
        self.effect_on_others = effect_on_others
        self.clock_event = None

    def activate(self, player_id, players):
        current_perk = players[player_id].perk
        current_perk.cancel(player_id, players)
        Clock.unschedule(self.clock_event)
        for i, p in enumerate(players):
            if i != player_id:
                p.effects.append(self.effect_on_others)

    def cancel(self, player_id, players):
        players[player_id].perk = None
        for i, p in enumerate(players):
            if i != player_id:
                p.effects.remove(self.effect_on_others)

    class Name(Enum):
        IMMOBILISE_ENEMIES = 'immobilise_enemies'
        ENEMIES_INVISIBLE = 'enemies_invisible'
        DOUBLE_POINTS = 'double_points'
        ADDITIONAL_MINE = 'additional_mine'
        ADDITIONAL_LIFE = 'additional_life'
        KILL_ENEMIES_ON_BAD_FLAG = 'kill_on_bad_flag'

    class Effect(Enum):
        IMMOBILISED = 0
        INVISIBLE = 1
        KILL_ON_BAD_FLAG = 2
        INVERSE_CONTROL = 3


class PerkManager:
    def __init__(self):
        self.perks = [
            (Perk(Perk.Name.DOUBLE_POINTS, None), 0.5),
            (Perk(Perk.Name.ENEMIES_INVISIBLE, Perk.Effect.INVISIBLE), 0.5)
        ]

    def random_perk(self):
        random = uniform(0, 1)
        acc = 0.0
        for perk in self.perks:
            acc += perk[1]
            if random < acc:
                return perk[0]
