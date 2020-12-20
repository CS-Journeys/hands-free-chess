import numpy as np
import time

from app import ChessUI
from src import command_recognition as cmd_recog
from src import board_recognition as b_recog
from src import board_manager as b_manager
from src import mouse_controller
from src import chess_piece

BOARD_CHECK_PAUSE_TIME = 1.5  # time (in seconds) to wait before rechecking for board

# Variable Initialization
board_data = np.full((8,8), chess_piece.ChessPiece('unknown', 'unknown'))
user_color = []

def setup(ui):
    # Adjust microphone for ambient noise
    cmd_recog.adjust_for_ambient_noise(2.0)

def ask_for_color(ui):
    global user_color
    # Listen for color until a valid piece color is provided - black or white
    ChessUI.print_to_user(ui, "Listening. What's your piece color?")
    user_command = cmd_recog.get_voice_command()
    while user_command != ['white'] and user_command != ['black']: 
        user_command = cmd_recog.get_voice_command()
    user_color = user_command[0]
    return user_color

def handle_user_command(ui):
    global user_color, board_data
    user_command = cmd_recog.get_voice_command()

    # Proceed if command contains at least 3 parts (minimum num for a valid cmd)
    if (len(user_command) >= 3):
        board_coords = b_recog.get_board_coords()

        # If board not detected, loop until board is detected
        while (board_coords == None):
            ChessUI.print_to_user(ui, "Board not detected. Searching again.")
            time.sleep(BOARD_CHECK_PAUSE_TIME)
            board_coords = b_recog.get_board_coords()
        
        # Identify each piece on board
        for row in range(1, 8 + 1):
            for col in range(1, 8 + 1):
                board_data[row - 1][col - 1] = b_recog.identify_piece(col, row)

        # Notify user if move is ambiguous
        if (b_manager.is_ambiguous_move(user_command, user_color, board_data)):
            ChessUI.print_to_user(ui, "Ambiguous move. Please repeat and specify which "
                             + str(b_manager.extract_piece_name(user_command))
                             + " you want to move.")
            
        # If move is legal and unambiguous, move piece with mouse
        elif (b_manager.is_legal_move(user_command, user_color, board_data)):
            initial_position = b_manager.get_initial_position(user_command, user_color, board_data)
            final_position = b_manager.get_final_position(user_command, user_color, board_data)
            mouse_controller.move_piece(initial_position, final_position, board_coords)
            
        # Notify user if move is illegal
        else:
            ChessUI.print_to_user(ui, "Illegal move! Try again.")

        # TO-DO: check for game over

        # DELETE ME (this is just for debugging)
        formatted_board_data = format_board_matrix(board_data)
        print(formatted_board_data)

    return user_command



# Useful helper function for aesthetic debugging <3, delete later
def format_board_matrix(board_matrix):
    for i in range(0, board_matrix.shape[0]):
        for j in range(0, board_matrix.shape[1]):
            if board_matrix[i,j] == "king":
                board_matrix[i,j] = "K"
            if board_matrix[i,j] == "empty":
                board_matrix[i,j] = " "
            board_matrix[i,j] = board_matrix[i,j].name[0]
    return board_matrix
