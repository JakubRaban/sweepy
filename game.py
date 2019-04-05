from board import Board
from player import Player


class Game:
    def __init__(self,rows,columns,nb_of_players):
        self.board = Board(rows,columns)
        self.players = []
        for index in range(nb_of_players):
            player = None
            if index == 0:
                player = Player(rows-1,0)
            elif index == 1:
                player = Player(0,columns-1)
            elif index == 2:
                player = Player(0, 0)
            elif index == 3:
                player = Player(rows - 1, columns - 1)
            if player is not None:
                self.players.append(player)

    def get_all_players_coords(self):
        return [(player.row, player.column) for player in self.players]

    def can_move_to(self,row,column):
        return self.board.can_move_to(row,column) and not (row, column) in self.get_all_players_coords()

    def move_player(self,player_id,move_direction):
        moving_player = self.players[player_id]
        coords = self.board.get_cell_towards(moving_player.row, moving_player.column, move_direction)
        if self.can_move_to(coords[0],coords[1]):
            self.players[player_id].set_new_position(coords)