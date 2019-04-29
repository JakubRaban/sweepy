
from enum import Enum


class Player:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.score = 0
        self.is_dead = False
        self.color = color

    def set_new_position(self, coords):
        self.row, self.column = coords[0], coords[1]

    def get_position(self):
        return self.row, self.column

    def add_points(self, delta):
        self.score += delta


class PlayerColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
