
class Player:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.score = 0
        self.is_dead = False

    def set_new_position(self, coords):
        self.row, self.column = coords[0], coords[1]

    def get_position(self):
        return self.row, self.column

    def add_points(self, delta):
        self.score += delta
