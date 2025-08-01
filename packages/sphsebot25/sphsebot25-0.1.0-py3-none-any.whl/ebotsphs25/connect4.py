import numpy as np

ROWS = 8
COLS = 8
PLAYER = 1
AI = 2
EMPTY = 0
WINDOW_LENGTH = 4
MAX_DEPTH = 4

def create_board():
    return np.zeros((ROWS, COLS), dtype=int)

def is_valid_location(board, col):
    return board[0][col] == EMPTY

def get_next_open_row(board, col):
    for r in reversed(range(ROWS)):
        if board[r][col] == EMPTY:
            return r

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def print_board(board):
    display = {0: '.', 1: 'O', 2: 'X'}
    for row in board:
        print(" ".join(display[val] for val in row))
    print("0 1 2 3 4 5 6 7")

def winning_move(board, piece):
    # Check all directions for win
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == piece for i in range(WINDOW_LENGTH)):
                return True
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r+i][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r-i][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True
    return False

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER if piece == AI else AI
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 5
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 8
    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in board[:, COLS//2]]
    score += center_array.count(piece) * 3

    # Horizontal
    for r in range(ROWS):
        row_array = list(board[r])
        for c in range(COLS - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Vertical
    for c in range(COLS):
        col_array = list(board[:, c])
        for r in range(ROWS - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Positive diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Negative diagonal
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    return [c for c in range(COLS) if is_valid_location(board, c)]

def is_terminal_node(board):
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI):
                return (None, 100000000)
            elif winning_move(board, PLAYER):
                return (None, -100000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI))

    if maximizingPlayer:
        value = -np.inf
        best_col = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI)
            _, new_score = minimax(temp_board, depth-1, alpha, beta, False)
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = np.inf
        best_col = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER)
            _, new_score = minimax(temp_board, depth-1, alpha, beta, True)
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# Game loop
board = create_board()
game_over = False
turn = 0  # 0 for player, 1 for AI

print_board(board)

while not game_over:
    if turn == 0:
        col = int(input("Player turn [0-7]: "))
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, PLAYER)
            if winning_move(board, PLAYER):
                print_board(board)
                print("🎉 You win!")
                game_over = True
    else:
        col, _ = minimax(board, MAX_DEPTH, -np.inf, np.inf, True)
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI)
            print(f"AI drops at column {col}")
            if winning_move(board, AI):
                print_board(board)
                print("💻 AI wins!")
                game_over = True
    print_board(board)
    turn ^= 1
