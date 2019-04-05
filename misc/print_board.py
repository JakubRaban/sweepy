
from board import Board

b = Board(10, 10)
b.spawn_mines()
b.assign_number_of_mines_around_to_cells()
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
