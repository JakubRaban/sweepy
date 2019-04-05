from board import Cell, ActionOutcome


class Player:
    def __init__(self,row,column):
        self.row = row
        self.column = column
        self.scores = 0
        self.is_dead = False

    def set_new_position(self,coords):
        self.row = coords[0]
        self.column = coords[1]

    def move_toward(self, board, move_direction):
        coords = board.get_cell_towards(self=self.cell, move_direction=move_direction)
        new_cell = Cell(coords[0],coords[1])
        self.cell = new_cell

    def flag_cell(self):
        status = self.cell.toggle_flag(self)
        if status == ActionOutcome.FLAG_CORRECT:
            self.scores+=1
        elif status == ActionOutcome.FLAG_INCORRECT:
            self.scores-=5

    def uncover_cell(self, board):
        status = board.uncover_cell(row=self.cell.row, column=self.cell.column, player=self)
        if status == ActionOutcome.EXPLODED:
            self.is_dead = True