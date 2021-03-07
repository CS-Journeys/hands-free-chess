import logging.config
import yaml
import numpy as np

from src.board_recognition import BoardRecognizer
from src import chess_piece

try:
    with open('../config/log_config.yaml', 'r') as conf_file:
        log_cfg = yaml.safe_load(conf_file.read())
except IOError as e:
    print("Unable to open log config file\n==> " + str(e))
    exit(1)
try:
    logging.config.dictConfig(log_cfg)
except ValueError as e:
    print("Unable to load log configuration\n==> " + str(e))
    exit(1)


def format_board_matrix(board_matrix):
    for i in range(0, board_matrix.shape[0]):
        for j in range(0, board_matrix.shape[1]):
            board_matrix[i,j] = board_matrix[i,j].name[0]
    return board_matrix


a = ""
board_data = np.full((8,8), chess_piece.ChessPiece('unknown', 'unknown'))
recognizer = BoardRecognizer()

# Main Loop
while a != "q":
    
    # Get board coords
    board_coords = recognizer._get_board_coords()
    print("Board coords = " + str(board_coords))
    
    # Identify each piece on board
    if board_coords is not None:
        for row in range(1, 8+1):
            for col in range(1, 8+1):
                board_data[row-1][col-1] = recognizer._identify_piece(col, row)
    else:
        board_data = np.full((8,8), chess_piece.ChessPiece('unknown', 'unknown'))

    # Print board to shell
    formatted_board_data = format_board_matrix(board_data)
    print(formatted_board_data)

    a = input("\nEnter 'q' to quit, else enter anything: ")
