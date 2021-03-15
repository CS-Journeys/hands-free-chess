import pyautogui
import logging

def move_piece(start, end, board_coords):
    """
    This function moves a chess piece by clicking and dragging on the screen.

    Parameters:
        - start: a tuple of two integers with the first element as a column number, and the second a row number (0-7)
        - end: a tuple of two integers with the first element as a column number, and the second a column number (0-7)
        - board_coords: a tuple of two 9-element lists --
                        the first list contains the x pixel coordinates of each vertical line
                        the second list contains the y pixel coordinates of each horizontal line
    Output:
        - return: none
        - mouse: the mouse moves to the center of the 'start' location and then clicks and drags to the 'end' location
    """

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
