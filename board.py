from enum import Enum
from random import shuffle


class Board:
    def __init__(self, rows, columns, filling_ratio=0.17):
        self.rows = rows
        self.columns = columns
        self.cells = dict()
        for i in range(rows):
            for j in range(columns):
                self.cells[(i, j)] = Cell(i, j)
        self.total_number_of_mines = int(self.rows * self.columns * filling_ratio)
        self.remaining_mines = self.total_number_of_mines
        self.spawn_mines(self.total_number_of_mines)
        board_correct = self.assign_number_of_mines_around_to_cells()
        if not board_correct:
            self.__init__(rows, columns, filling_ratio)

    def spawn_mines(self, number_of_mines):
        all_coordinates = list(self.cells.keys())
        self.remove_corners_from_coordinates(all_coordinates)
        shuffle(all_coordinates)
        for i in range(number_of_mines):
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

    def uncover_cell(self, row, column, player, cells_to_update=[]):
        current_cell = self.get_cell_by_indexes(row, column)
        cells_to_update.append((row, column))
        uncover_status = current_cell.uncover(player)
        if uncover_status == ActionOutcome.UNCOVER_ZERO:
            adjacent_cells = self.get_adjacent_cells_coordinates(row, column)
            for cell in adjacent_cells:
                self.uncover_cell(cell[0], cell[1], player, cells_to_update)
        if uncover_status == ActionOutcome.EXPLODED:
            self.remaining_mines -= 1
        return uncover_status, cells_to_update

    def toggle_flag(self, row, column, player):
        outcome = self.get_cell_by_indexes(row, column).toggle_flag(player)
        if outcome == ActionOutcome.FLAG_CORRECT:
            self.remaining_mines -= 1
        return outcome

    def get_cell_by_indexes(self, row, column):
        return self.cells[(row, column)]

    def get_cell_with_tuple(self, coordinates):
        return self.cells[coordinates]

    def is_cell_present(self, row, column):
        return row in range(self.rows) and column in range(self.columns)

    def can_move_to(self, row, column):
        cell = self.get_cell_by_indexes(row, column)
        return cell.flagging_player is None or not cell.has_mine

    def get_cell_towards(self, row, column, move_direction, inversed_direction):
        direction_t = move_direction.value
        if inversed_direction:
            direction_t = tuple([-x for x in direction_t])
        new_coordinates = [sum(x) for x in zip((row, column), direction_t)]
        if not new_coordinates[0] in range(self.rows):
            new_coordinates[0] = abs(abs(new_coordinates[0]) - self.rows)
        if not new_coordinates[1] in range(self.columns):
            new_coordinates[1] = abs(abs(new_coordinates[1]) - self.columns)
        return tuple(new_coordinates)

    def get_adjacent_cells_coordinates(self, row, column):
        adjacent_cells = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if self.is_cell_present(row + i, column + j):
                    adjacent_cells.append((row + i, column + j))
        adjacent_cells.remove((row, column))
        return adjacent_cells

    def get_perkable_cells(self, players):
        return [cell for cell in list(self.cells.values())
                if not cell.is_uncovered
                and cell.perk is None
                and cell.flagging_player is None
                and not cell.get_position() in [player.get_position() for player in players]]


class Cell:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.has_mine = False
        self.has_mine_from_start = True
        self.mines_around = 0
        self.is_uncovered = False
        self.flagging_player = None
        self.perk = None

    def uncover(self, player):
        if self.is_uncovered or self.flagging_player is not None:
            return ActionOutcome.NO_OUTCOME
        self.is_uncovered = True
        self.perk = None
        if self.has_mine:
            return ActionOutcome.EXPLODED
        else:
            if self.mines_around == 0:
                return ActionOutcome.UNCOVER_ZERO
            else:
                return ActionOutcome.UNCOVER_CORRECT

    def toggle_flag(self, player):
        if self.flagging_player is not None and not self.has_mine:
            self.flagging_player = None
        elif not self.is_uncovered:
            self.flagging_player = player
            if self.has_mine:
                return ActionOutcome.FLAG_CORRECT
            else:
                return ActionOutcome.FLAG_INCORRECT
        return ActionOutcome.NO_OUTCOME

    def get_position(self):
        return self.row, self.column


class ActionOutcome(Enum):
    NO_OUTCOME = 0
    FLAG_CORRECT = 1
    FLAG_INCORRECT = 2
    UNCOVER_CORRECT = 3
    UNCOVER_ZERO = 4
    EXPLODED = 5


class MoveDirection(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
