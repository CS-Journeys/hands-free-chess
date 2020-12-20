######################################################################
# PARAMETER DOCUMENTATION
#
# board_coords is a tuple of two 9-element lists
#   first list contains the x coordinates of each vertical line
#   second list contains the y coordinates of each horizontal line
#
# start is a 2-element tuple
#   first element is the column number (0-7)
#   second element is the row number   (0-7)
#
# end is also a 2-element tuple
#   first element is the column number (0-7)
#   second element is the row number   (0-7)
#
######################################################################

import pyautogui
import logging

def move_piece(start, end, board_coords):
    # Define the actual coordinates for the mouse. Rounded just in case partial pixels are frowned upon.
    # Just takes the arithmetic mean of the vertical/horizontal boundaries of the square to find the approximate center
    # to click.
    x_start = round((board_coords[0][start[0]] + board_coords[0][start[0]+1]) / 2)
    y_start = round((board_coords[1][start[1]] + board_coords[1][start[1]+1]) / 2)

    x_end = round((board_coords[0][end[0]] + board_coords[0][end[0]+1]) / 2)
    y_end = round((board_coords[1][end[1]] + board_coords[1][end[1]+1]) / 2)

    pyautogui.click(x_start, y_start)
    pyautogui.dragTo(x_end, y_end, button='left')

    log = logging.getLogger(__name__)
    log.debug(f"Moved mouse from ({x_start}, {y_start}) to ({x_end},{y_end})")
