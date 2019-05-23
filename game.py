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
        self.window = None
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
        Clock.schedule_once(lambda dt: self.perk_event(), uniform(20, 40))

    def perk_event(self):
        perked_cell = self.put_perk_on_board()
        if perked_cell is not None:
            self.window.game_grid.update_cell(perked_cell[0], perked_cell[1], self)
        Clock.schedule_once(lambda dt: self.perk_event(), uniform(20, 40))

    def get_all_players_coords(self):
        return [(player.row, player.column) for player in self.players]

    def can_move_to(self, row, column):
        return self.board.can_move_to(row, column) and not (row, column) in self.get_all_players_coords()

    def move_player(self, player_id, move_direction):
        moving_player = self.players[player_id]
        coords = self.board.get_cell_towards(moving_player.row, moving_player.column, move_direction,
                                             inversed_direction=self.players[player_id].has_effect(Perk.Effect.INVERSE_CONTROL))
        if self.can_move_to(coords[0], coords[1]) and self.able_to_move(player_id):
            self.players[player_id].set_new_position(coords)
            new_perk = self.board.cells[coords].perk
            if new_perk is not None:
                self.collect_perk(new_perk, player_id)
                self.board.cells[coords].perk = None

    def able_to_move(self, player_id):
        return not self.players[player_id].is_dead and not self.players[player_id].has_effect(Perk.Effect.IMMOBILISED)

    def uncover_cell(self, player_id):
        current_player = self.players[player_id]
        player_position = current_player.get_position()
        uncover_outcome = self.board.uncover_cell(player_position[0], player_position[1], current_player)
        if uncover_outcome == ActionOutcome.EXPLODED:
            if self.players[player_id].has_perk(Perk.Name.ADDITIONAL_LIFE):
                PerkManager.empty_perk.activate(player_id, self.players)
            else:
                current_player.is_dead = True

    def flag_cell(self, player_id):
        current_player = self.players[player_id]
        player_position = current_player.get_position()
        flagging_outcome = self.board.toggle_flag(player_position[0], player_position[1], current_player)
        if flagging_outcome == ActionOutcome.FLAG_CORRECT:
            points_to_add = 1
            if self.players[player_id].has_perk(Perk.Name.DOUBLE_POINTS):
                points_to_add += 1
            current_player.add_points(points_to_add)
        elif flagging_outcome == ActionOutcome.FLAG_INCORRECT:
            if not current_player.has_effect(Perk.Effect.KILL_ON_BAD_FLAG):
                current_player.add_points(-5)
            else:
                current_player.is_dead = True

    def drop_item(self, player_id):
        current_player = self.players[player_id]
        player_position = current_player.get_position()
        if current_player.has_perk(Perk.Name.DROP_MINE):
            if not self.board.get_cell_with_tuple(player_position).has_mine:
                self.board.get_cell_with_tuple(player_position).has_mine = True
                self.board.remaining_mines += 1
            PerkManager.empty_perk.activate(player_id, self.players)
        if current_player.has_perk(Perk.Name.LOOK_ASIDE):
            cells_around = self.board.get_adjacent_cells_coordinates(player_position[0], player_position[1])
            affected_cells = cells_around + [player_position]
            for cell_position in affected_cells:
                if not self.board.get_cell_with_tuple(cell_position).has_mine:
                    self.board.uncover_cell(cell_position[0], cell_position[1], player_id)
            PerkManager.empty_perk.activate(player_id, self.players)

    def all_players_dead(self):
        return len([player.is_dead for player in self.players if not player.is_dead]) == 0

    def is_finished(self):
        return self.board.remaining_mines == 0 or self.all_players_dead()

    def put_perk_on_board(self):
        possible_cells = self.board.get_perkable_cells(self.players)
        if len(possible_cells) == 0:
            return None
        shuffle(possible_cells)
        cell_to_perk = possible_cells[0]
        cell_to_perk.perk = self.perk_manager.random_perk()
        return cell_to_perk.row, cell_to_perk.column

    def collect_perk(self, perk, player_id):
        perk.activate(player_id, self.players)
        perk_lasting_time = uniform(10, 20)
        perk.clock_event = Clock.schedule_once(lambda dt: perk.cancel(player_id, self.players), perk_lasting_time)
        Clock.schedule_once(lambda dt: self.window.update_labels(), perk_lasting_time)
        self.window.update_labels()


class Perk:
    def __init__(self, name, effect_on_others):
        self.name = name
        self.effect_on_others = effect_on_others
        self.clock_event = None

    def activate(self, player_id, players):
        current_perk = players[player_id].perk
        if current_perk is not None and current_perk.clock_event is not None:
            current_perk.clock_event.cancel()
        if current_perk is not None:
            current_perk.cancel(player_id, players)
        if self.name is not None:
            players[player_id].perk = self
        else:
            players[player_id].perk = None
        for i, p in enumerate(players):
            if i != player_id:
                p.effects.append(self.effect_on_others)

    def cancel(self, player_id, players):
        if self.effect_on_others is not None:
            for i, p in enumerate(players):
                if i != player_id:
                    p.effects.remove(self.effect_on_others)
        players[player_id].perk = None

    class Name(Enum):
        IMMOBILISE_ENEMIES = 'immobilise_enemies'
        ENEMIES_INVISIBLE = 'enemies_invisible'
        DOUBLE_POINTS = 'double_points'
        DROP_MINE = 'drop_mine'
        ADDITIONAL_LIFE = 'additional_life'
        KILL_ENEMIES_ON_BAD_FLAG = 'kill_on_bad_flag'
        LOOK_ASIDE = 'look_aside'
        INVERSE_CONTROL_FOR_ENEMIES = 'inverse_control'

    class Effect(Enum):
        IMMOBILISED = 0
        INVISIBLE = 1
        KILL_ON_BAD_FLAG = 2
        INVERSE_CONTROL = 3


class PerkManager:
    empty_perk = Perk(None, None)

    def __init__(self):
        self.perks = [
            (Perk.Name.DOUBLE_POINTS, None, 1/8),
            (Perk.Name.ENEMIES_INVISIBLE, Perk.Effect.INVISIBLE, 1/8),
            (Perk.Name.IMMOBILISE_ENEMIES, Perk.Effect.IMMOBILISED, 1/8),
            (Perk.Name.ADDITIONAL_LIFE, None, 1/8),
            (Perk.Name.KILL_ENEMIES_ON_BAD_FLAG, Perk.Effect.KILL_ON_BAD_FLAG, 1/8),
            (Perk.Name.DROP_MINE, None, 1/8),
            (Perk.Name.LOOK_ASIDE, None, 1/8),
            (Perk.Name.INVERSE_CONTROL_FOR_ENEMIES, Perk.Effect.INVERSE_CONTROL, 1/8)
        ]

    def random_perk(self):
        random = uniform(0, 1)
        acc = 0.0
        for perk_desc in self.perks:
            acc += perk_desc[2]
            if random < acc:
                return Perk(perk_desc[0], perk_desc[1])
