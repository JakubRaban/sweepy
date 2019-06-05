from enum import Enum


class Player:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.score = 0
        self.is_dead = False
        self.color = color
        self.perk = None
        self.effects = list()

    def set_new_position(self, coords):
        self.row, self.column = coords[0], coords[1]

    def get_position(self):
        return self.row, self.column

    def add_points(self, delta):
        self.score += delta

    def has_perk(self, perk_name):
        return self.perk and self.perk.name == perk_name

    def has_effect(self, effect):
        return effect in self.effects


class PlayerColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
