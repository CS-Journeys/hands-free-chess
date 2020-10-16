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

def move_piece(start, end, board_coords):
    # FIXME
    pyautogui.moveTo(100, 400)
