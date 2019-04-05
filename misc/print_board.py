
from board import Board

b = Board(16, 16, 0.22)
for k in range(b.rows):
    for l in range(b.columns):
        cell = b.get_cell_by_indexes(k, l)
        if cell.has_mine:
            print('-', end=' ')
        elif cell.mines_around == 0:
            print(' ', end=' ')
        elif cell.mines_around > 0:
            print(cell.mines_around, end=' ')
    print()
