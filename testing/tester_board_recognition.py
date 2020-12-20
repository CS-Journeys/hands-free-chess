import sys
sys.path.append("../")

import time
from src.board_recognition import *
from src import chess_piece


def format_board_matrix(board_matrix):
    for i in range(0, board_matrix.shape[0]):
        for j in range(0, board_matrix.shape[1]):
            board_matrix[i,j] = board_matrix[i,j].name[0]
    return board_matrix

a = ""
board_data = np.full((8,8), chess_piece.ChessPiece('unknown', 'unknown'))


# Main Loop
while a != "q":
    
    # Get board coords
    board_coords = get_board_coords()
    print("Board coords = " + str(board_coords))
    
    # Identify each piece on board
    if board_coords != None:
        for row in range(1, 8+1):
            for col in range(1, 8+1):
                board_data[row-1][col-1] = identify_piece(col,row)
    else:
        board_data = np.full((8,8), chess_piece.ChessPiece('unknown', 'unknown'))

    # Print board to shell
    formatted_board_data = format_board_matrix(board_data)
    print(formatted_board_data)

    a = input("\nEnter 'q' to quit, else enter anything: ")
