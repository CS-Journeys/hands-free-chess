import os
import numpy as np
import time
import logging
import logging.config
import yaml
import app
from src import command_recognition as cmd_recog
from src import board_recognition
from src import board_manager
from src import mouse_controller
from src import chess_piece

BOARD_CHECK_PAUSE_TIME = 1.5  # time (in seconds) to wait before rechecking for board
LOG_CONF_FILE = 'log_config.yaml'
log = logging.getLogger(__name__)
b_recog = board_recognition.BoardRecognizer()
b_manager = board_manager.BoardManager()

# Variable Initialization
board_data = np.full((8,8), chess_piece.ChessPiece('unknown', 'unknown'))
user_color = []

def setup(ui):
    # Adjust microphone for ambient noise
    log.info("Adjusting microphone for ambient noise")
    cmd_recog.adjust_for_ambient_noise(2.0)

def ask_for_color(ui):
    global user_color
    # Listen for color until a valid piece color is provided - black or white
    app.print_to_user(ui, "Listening. What's your piece color?")
    user_command = cmd_recog.get_voice_command()
    while user_command != ['white'] and user_command != ['black']:
        user_command = cmd_recog.get_voice_command()
    user_color = user_command[0]
    log.info(f"Piece color: {user_color}")
    return user_color

def handle_user_command(ui):
    global user_color, board_data
    log.info("Listening for command")
    user_command = cmd_recog.get_voice_command()
    log.info(f"Command: {user_command}")

    # Proceed if command contains at least 3 parts (minimum num for a valid cmd)
    if len(user_command) >= 3:
        log.info("Searching for board")
        board_coords = b_recog.get_board_coords()

        # If board not detected, loop until board is detected
        while board_coords == None:
            log.info("Searching for board again")
            app.print_to_user(ui, "Board not detected. Searching again.")
            time.sleep(BOARD_CHECK_PAUSE_TIME)
            board_coords = b_recog.get_board_coords()

        # Identify each piece on board
        log.info("Identifying pieces")
        for row in range(1, 8 + 1):
            for col in range(1, 8 + 1):
                board_data[row - 1][col - 1] = b_recog.identify_piece(col, row)

        # Notify user if move is ambiguous
        log.info("Checking ambiguity")
        if b_manager.is_ambiguous_move(user_command, user_color, board_data):
            app.print_to_user(ui, "Ambiguous move. Please repeat and specify which " + str(b_manager.extract_piece_name(user_command)) + " you want to move.")

        # If move is legal and unambiguous, move piece with mouse
        log.info("Checking legality")
        elif b_manager.is_legal_move([user_command, user_color, board_data]):
            log.info(f"OK! Moving {b_manager.extract_piece_name(user_command)}"
                 f" to {user_command[-2]}{user_command[-1]}")
            initial_position = b_manager.get_initial_position(user_command, user_color, board_data)
            final_position = b_manager.get_final_position(user_command, user_color, board_data)
            mouse_controller.move_piece(initial_position, final_position, board_coords)

        # Notify user if move is illegal
        else:
            log.warning(f"{user_command} is illegal")
            app.print_to_user(ui, "Illegal move! Try again.")

        # TO-DO: check for game over

        # DELETE ME (this is just for debugging)
        formatted_board_data = format_board_matrix(board_data)
        log.info(f"Formatted board data:\n{formatted_board_data}")
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


# Load logging configuration from file
def configure_logging():
    if not os.path.exists('log'):
        os.makedirs('log')

    try:
        with open(LOG_CONF_FILE, 'r') as conf_file:
            log_cfg = yaml.safe_load(conf_file.read())
    except IOError as e:
        print("Unable to open log config file\n==> " + str(e))
        exit(1)
    try:
        logging.config.dictConfig(log_cfg)
    except ValueError as e:
        print("Unable to load log configuration\n==> " + str(e))
        exit(1)