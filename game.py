
from random import shuffle
from board import Board, ActionOutcome
from player import Player, PlayerColor


class Game:
    def __init__(self, rows, columns, nb_of_players):
        self.board = Board(rows, columns)
        self.players = []
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
            if self.board.cells[coords].perk is not None:
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

    def put_perk(self):
        possible_cells = self.board.get_covered_cells()
        if len(possible_cells) == 0:
            return None
        shuffle(possible_cells)
        cell_to_perk = possible_cells[0]
        cell_to_perk.perk = 'p'
        return cell_to_perk.row, cell_to_perk.column
