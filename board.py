
from random import shuffle


class Board:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.mines_spawned = False
        self.cells = dict()
        for i in range(rows):
            for j in range(columns):
                self.cells.update({(i, j): Cell(i, j)})

    def spawn_mines(self, filling_ratio=0.16):
        if not self.mines_spawned:
            all_coordinates = list(self.cells.keys())
            shuffle(all_coordinates)
            for i in range(int(self.rows * self.columns * filling_ratio)):
                self.cells[all_coordinates[i]].has_mine = True


class Cell:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.has_mine = False
        self.mines_around = 0

    def adjacent_cells_coordinates(self, board_size_rows, board_size_columns):
        adjacent_cells = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if self.row + i in range(board_size_rows) and self.column + j in range(board_size_columns):
                    adjacent_cells.append((self.row + i, self.column + j))
        adjacent_cells.remove((self.row, self.column))
        return adjacent_cells

