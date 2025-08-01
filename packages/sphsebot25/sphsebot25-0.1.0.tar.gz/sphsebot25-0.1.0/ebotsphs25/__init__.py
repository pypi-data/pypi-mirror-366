# smartgames/__init__.py

# From bfs.py
from .bfs import solve_maze

# From connect4.py
from .connect4 import (
    create_board,
    is_valid_location,
    get_next_open_row,
    drop_piece,
    print_board as print_connect4_board,
    winning_move,
    evaluate_window,
    score_position,
    get_valid_locations,
    is_terminal_node,
    minimax as connect4_minimax
)

# From maze.py
from .maze import visualize_maze

# From pattern.py
from .pattern import logic_predict, symbol_predict_and_encode

# From tictactoe.py
from .tictactoe import (
    print_board as print_tictactoe_board,
    check_winner,
    check_draw,
    get_available_moves,
    minimax as tictactoe_minimax,
    player_move,
    computer_move,
    main as tictactoe_main
)
