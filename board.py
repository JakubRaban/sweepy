
from random import shuffle


class Board:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.mines_spawned = False
        self.cells = dict()
        for i in range(rows):
            for j in range(columns):
                self.cells[(i, j)] = Cell(i, j)
        self.spawn_mines()
        self.assign_number_of_mines_around_to_cells()

    def spawn_mines(self, filling_ratio=0.16):
        if not self.mines_spawned:
            all_coordinates = list(self.cells.keys())
            shuffle(all_coordinates)
            for i in range(int(self.rows * self.columns * filling_ratio)):
                self.cells[all_coordinates[i]].has_mine = True

    def assign_number_of_mines_around_to_cells(self):
        for coordinate, cell in self.cells.items():
            if cell.has_mine:
                adjacent_cells_coordinates = cell.get_adjacent_cells_coordinates(self.rows, self.columns)
                for adj in adjacent_cells_coordinates:
                    self.get_cell_with_tuple(adj).mines_around += 1

    def uncover_cell(self, row, column, player):
        current_cell = self.get_cell_by_indexes(row, column)
        uncover_status = current_cell.uncover(player)
        if uncover_status is ActionOutcome.UNCOVER_ZERO:
            adjacent_cells = current_cell.get_adjacent_cells_coordinates(self.rows, self.columns)
            for cell in adjacent_cells:
                self.uncover_cell(cell[0], cell[1], player)
        return ActionOutcome.UNCOVER_CORRECT

    def toggle_flag(self, row, column, player):
        return self.get_cell_by_indexes(row, column).toggle_flag(player)

    def get_cell_by_indexes(self, row, column):
        return self.cells[(row, column)]

    def get_cell_with_tuple(self, coordinates):
        return self.cells[coordinates]


class Cell:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.has_mine = False
        self.mines_around = 0
        self.is_uncovered = False
        self.flagging_player = None

    def get_adjacent_cells_coordinates(self, board_size_rows, board_size_columns):  # Czy można to zamienić na generator?
        adjacent_cells = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if self.row + i in range(board_size_rows) and self.column + j in range(board_size_columns):
                    adjacent_cells.append((self.row + i, self.column + j))
        adjacent_cells.remove((self.row, self.column))
        return adjacent_cells
