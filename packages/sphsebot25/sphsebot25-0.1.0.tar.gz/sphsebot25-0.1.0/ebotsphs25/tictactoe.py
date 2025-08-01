import random

def print_board(board):
    print("\n")
    for i in range(3):
        print(" ".join(board[i * 3:(i + 1) * 3]))
    print("\n")

def check_winner(board):
    lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def check_draw(board):
    return all(cell != " " for cell in board) and check_winner(board) is None

def get_available_moves(board):
    return [i for i in range(9) if board[i] == " "]

def minimax(board, is_maximizing):
    winner = check_winner(board)
    if winner == "O":
        return 1, None
    elif winner == "X":
        return -1, None
    elif check_draw(board):
        return 0, None

    best_score = float('-inf') if is_maximizing else float('inf')
    best_move = None

    for move in get_available_moves(board):
        board[move] = "O" if is_maximizing else "X"
        score, _ = minimax(board, not is_maximizing)
        board[move] = " "

        if is_maximizing:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

    return best_score, best_move

def player_move(board):
    while True:
        try:
            move = int(input("Choose your move (1-9): ")) - 1
            if move in get_available_moves(board):
                return move
            else:
                print("Invalid move. Try again.")
        except ValueError:
            print("Enter a number between 1 and 9.")

def computer_move(board):
    _, move = minimax(board, True)
    return move

def main():
    board = [" "] * 9
    print_board(board)

    while True:
        move = player_move(board)
        board[move] = "X"
        print_board(board)
        if check_winner(board):
            print("You win!")
            break
        if check_draw(board):
            print("It's a draw.")
            break

        move = computer_move(board)
        board[move] = "O"
        print_board(board)
        if check_winner(board):
            print("Computer wins.")
            break
        if check_draw(board):
            print("It's a draw.")
            break

