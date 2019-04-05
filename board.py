
from enum import Enum
from random import shuffle


class Board:
    def __init__(self, rows, columns, filling_ratio=0.16):
        self.rows = rows
        self.columns = columns
        self.mines_spawned = False
        self.cells = dict()
        for i in range(rows):
            for j in range(columns):
                self.cells[(i, j)] = Cell(i, j)
        self.spawn_mines(filling_ratio)
        board_correct = self.assign_number_of_mines_around_to_cells()
        if not board_correct:
            self.__init__(rows, columns, filling_ratio)

    def spawn_mines(self, filling_ratio=0.16):
        if not self.mines_spawned:
            all_coordinates = list(self.cells.keys())
            self.remove_corners_from_coordinates(all_coordinates)
            shuffle(all_coordinates)
            for i in range(int(self.rows * self.columns * filling_ratio)):
                self.cells[all_coordinates[i]].has_mine = True

    def remove_corners_from_coordinates(self, all_coordinates):
        for i in [0, 1, self.rows - 1, self.rows - 2]:
            for j in [0, 1, self.columns - 1, self.columns - 2]:
                all_coordinates.remove((i, j))

    def assign_number_of_mines_around_to_cells(self):
        for coordinate, cell in self.cells.items():
            if cell.has_mine:
                adjacent_cells_coordinates = self.get_adjacent_cells_coordinates(coordinate[0], coordinate[1])
                for adj in adjacent_cells_coordinates:
                    filled_cell = self.get_cell_with_tuple(adj)
                    filled_cell.mines_around += 1
                    if filled_cell.mines_around == 8 and filled_cell.has_mine:
                        return False
        return True

    def uncover_cell(self, row, column, player):
        current_cell = self.get_cell_by_indexes(row, column)
        uncover_status = current_cell.uncover(player)
        if uncover_status == ActionOutcome.UNCOVER_ZERO:
            adjacent_cells = self.get_adjacent_cells_coordinates(row, column)
            for cell in adjacent_cells:
                self.uncover_cell(cell[0], cell[1], player)
            return ActionOutcome.UNCOVER_CORRECT
        return uncover_status

    def toggle_flag(self, row, column, player):
        return self.get_cell_by_indexes(row, column).toggle_flag(player)

    def get_cell_by_indexes(self, row, column):
        return self.cells[(row, column)]

    def get_cell_with_tuple(self, coordinates):
        return self.cells[coordinates]

    def is_cell_present(self, row, column):
        return row in range(self.rows) and column in range(self.columns)

    def get_cell_towards(self, row, column, move_direction):
        new_coordinates = [sum(x) for x in zip((row, column), move_direction.value)]
        if not new_coordinates[0] in range(self.rows):
            new_coordinates[0] = abs(abs(new_coordinates[0]) - self.rows)
        if not new_coordinates[1] in range(self.columns):
            new_coordinates[1] = abs(abs(new_coordinates[1]) - self.columns)
        return new_coordinates

    def get_adjacent_cells_coordinates(self, row, column):  # Czy można to zamienić na generator?
        adjacent_cells = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if self.is_cell_present(row + i, column + j):
                    adjacent_cells.append((row + i, column + j))
        adjacent_cells.remove((row, column))
        return adjacent_cells


class Cell:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.has_mine = False
        self.mines_around = 0
        self.is_uncovered = False
        self.flagging_player = None

    def uncover(self, player):
        if self.is_uncovered or self.flagging_player is not None:
            return ActionOutcome.NO_OUTCOME
        self.flagging_player = player
        self.is_uncovered = True
        if not self.has_mine:
            return ActionOutcome.EXPLODED
        else:
            if self.mines_around == 0:
                return ActionOutcome.UNCOVER_ZERO
            else:
                return ActionOutcome.UNCOVER_CORRECT

    def toggle_flag(self, player):
        if self.flagging_player is not None:
            self.flagging_player = None
            return ActionOutcome.NO_OUTCOME
        else:
            self.flagging_player = player
            if self.has_mine:
                return ActionOutcome.FLAG_CORRECT
            else:
                return ActionOutcome.FLAG_INCORRECT


class ActionOutcome(Enum):
    NO_OUTCOME = 0
    FLAG_CORRECT = 1
    FLAG_INCORRECT = 2
    UNCOVER_CORRECT = 3
    UNCOVER_ZERO = 4
    EXPLODED = 5


class MoveDirection(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (0, 1)
