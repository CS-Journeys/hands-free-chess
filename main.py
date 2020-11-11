import numpy as np
import time

from src import command_recognition as cmd_recog
from src import board_recognition as b_recog
from src import board_manager as b_manager
from src import user_interface as ui
from src import mouse_controller

BOARD_CHECK_PAUSE_TIME = 1.5 # time (in seconds) to wait before rechecking for board

def main():

    # Variable initialization
    board_data = np.full((8,8), 'unknown')
    user_command = []

    # Adjust microphone for ambient noise
    ui.print_to_user("Please wait...")
    cmd_recog.adjust_for_ambient_noise(2.0)
    ui.print_to_user("Listening. What's your move?")

    # Main loop (CTRL + C To Exit)
    while user_command != ['exit']:
        user_command.extend(cmd_recog.get_voice_commands())

        # Proceed if command contains at least 3 parts (minimum num for a valid cmd)
        if (len(user_command) >= 3):
            board_coords = b_recog.get_board_coords()

            # If board not detected, loop until board is detected
            while (board_coords == None):
                ui.print_to_user("Board not detected. Searching again.")
                time.sleep(BOARD_CHECK_PAUSE_TIME)
                board_coords = b_recog.get_board_coords()

            # Identify each piece on board
            for row in range(1, 8+1):
                for col in range(1, 8+1):
                    board_data[row-1][col-1] = b_recog.identify_piece(col,row)

            # If move is legal, move piece with mouse
            if (b_manager.is_legal_move(user_command, board_data)):
                initial_position = b_manager.get_initial_position(user_command, board_data)
                final_position = b_manager.get_final_position(user_command, board_data)
                mouse_controller.move_piece(initial_position, final_position, board_coords)
            else:
                ui.print_to_user("Illegal move! Try again.")
                pass

            # TO-DO: check for game over

            # DELETE ME (this is just for debugging)
            formatted_board_data = format_board_matrix(board_data)
            print(formatted_board_data)

            # Reset command before the next iteration
            user_command = []


# Useful helper function for aesthetic debugging <3, delete later
def format_board_matrix(board_matrix):
    board_matrix = np.where(board_matrix=="king", "K", board_matrix)
    board_matrix = np.where(board_matrix=="empty", " ", board_matrix)
    for i in range(0, board_matrix.shape[0]):
        for j in range(0, board_matrix.shape[1]):
            board_matrix[i,j] = board_matrix[i,j][0]
    return board_matrix

if __name__ == "__main__":
    main()
