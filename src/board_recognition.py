from PIL import ImageGrab
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pyautogui
from sklearn.neighbors.kde import KernelDensity
from scipy.signal import argrelextrema

from src import chess_piece

''' CUSTOM DATA TYPES '''
# A ConsecutivePixelColorSequence (cpcs) is a set of consecutive pixels
# in a row that have the same color value.
# Each cpcs has a color, start index, and length.
class ConsecutivePixelColorSequence:
    def __init__(self, color, start_pixel, length = 1):
        self.color = color
        self.start_pixel = start_pixel
        self.length = length

''' CONSTANTS '''
SCREEN_WIDTH  = pyautogui.size()[0]
SCREEN_HEIGHT = pyautogui.size()[1]
SCREEN_RATIO  = SCREEN_WIDTH / SCREEN_HEIGHT
SCALED_HEIGHT = 720 # arbitrary scaled down resolution to reduce computation time
REFERENCE_IMG_DIM = 33 # width and height in pixels
CHESS_PIECES = [chess_piece.ChessPiece('pawn', 'black'),
                chess_piece.ChessPiece('rook', 'black'),
                chess_piece.ChessPiece('knight', 'black'),
                chess_piece.ChessPiece('bishop', 'black'),
                chess_piece.ChessPiece('queen', 'black'),
                chess_piece.ChessPiece('king', 'black'),
                chess_piece.ChessPiece('pawn', 'white'),
                chess_piece.ChessPiece('rook', 'white'),
                chess_piece.ChessPiece('knight', 'white'),
                chess_piece.ChessPiece('bishop', 'white'),
                chess_piece.ChessPiece('queen', 'white'),
                chess_piece.ChessPiece('king', 'white'),
                chess_piece.ChessPiece('empty', 'empty')]

''' GLOBAL VARIABLES '''
scaled_col_coords = []
scaled_row_coords = []
frame = None


''' PUBLIC FUNCTIONS '''

# description  : Find the chessboard and its coordinates on the screen
# return       : two lists of floats
# precondition : None
# postcondition: If chessboard is detected, return the 9-elements lists
#                of vertical and horizontal line coordinates.
#                If chessboard is not detected, return None.
def get_board_coords():
    global frame, scaled_row_coords, scaled_col_coords

    frame = _get_processed_screenshot()
    ss_width  = frame.shape[1] #ss is short for screenshot
    ss_height = frame.shape[0]
    scaled_row_coords = []
    scaled_col_coords = []
    
    # FIND COLUMN COORDINATES
    col_coords_are_found = False
    i = round(ss_height / 4)
    while i < round((3/4) * ss_height) and not col_coords_are_found:

        # Split row into consecutive pixel color sequences
        consecutive_color_arr = [ConsecutivePixelColorSequence(frame[i,0], 0)]
        for j in range(1, ss_width):
            if frame[i,j] == consecutive_color_arr[-1].color:
                consecutive_color_arr[-1].length += 1
            else:
                consecutive_color_arr.append(ConsecutivePixelColorSequence(frame[i,j], j))

        # 'cpcs' stands for 'ConsecutivePixelColorSequence'
        # Cluster the cpcs's by length
        consecutive_color_arr_lengths = [sequence.length for sequence in consecutive_color_arr]
        cpcs_length_clusters = _cluster_objects(consecutive_color_arr, consecutive_color_arr_lengths)

        # Find checker pattern
        for cluster in cpcs_length_clusters:
            checker_pattern_start_index = _find_cpcs_checker_pattern(cluster)
            if checker_pattern_start_index != -1:
                col_coords_are_found = True
                
                # Set chessboard column pixel start
                first_cpcs = cluster[checker_pattern_start_index]
                actual_first_square_length = cluster[checker_pattern_start_index+1].start_pixel - first_cpcs.start_pixel
                pixel_offset = (actual_first_square_length - first_cpcs.length) / 2
                leftmost_chessboard_pixel = first_cpcs.start_pixel - pixel_offset

                # Set chessboard size
                chessboard_size = cluster[checker_pattern_start_index+7].start_pixel - cluster[checker_pattern_start_index].start_pixel
                chessboard_size = chessboard_size + (chessboard_size / 7) + 1

                # TO-DO: Programmatically fix this size bug instead of
                #        hardcoding a specific value
                chessboard_size -= 2
                break
        
        i += 1

    
    # FIND ROW COORDINATES
    if col_coords_are_found:
        row_coords_are_found = False
        i = round(leftmost_chessboard_pixel)
        while i < ss_width and not row_coords_are_found:

            # Split column into consecutive pixel color sequences
            consecutive_color_arr = [ConsecutivePixelColorSequence(frame[0,i], 0)]
            for j in range(1, ss_height):
                if frame[j,i] == consecutive_color_arr[-1].color:
                    consecutive_color_arr[-1].length += 1
                else:
                    consecutive_color_arr.append(ConsecutivePixelColorSequence(frame[j,i], j))

            # 'cpcs' stands for 'ConsecutivePixelColorSequence'
            # Cluster the cpcs's by length
            consecutive_color_arr_lengths = [sequence.length for sequence in consecutive_color_arr]
            cpcs_length_clusters = _cluster_objects(consecutive_color_arr, consecutive_color_arr_lengths)

            # Find checker pattern
            for cluster in cpcs_length_clusters:
                checker_pattern_start_index = _find_cpcs_checker_pattern(cluster)
                if checker_pattern_start_index != -1:
                    row_coords_are_found = True
                    
                    # Set chessboard row pixel start
                    first_cpcs = cluster[checker_pattern_start_index]
                    actual_first_square_length = cluster[checker_pattern_start_index+1].start_pixel - first_cpcs.start_pixel
                    pixel_offset = (actual_first_square_length - first_cpcs.length) / 2
                    upmost_chessboard_pixel = first_cpcs.start_pixel - pixel_offset

                    break
            
            i += 1

    
    # Set the coordinates of every grid line based on the chessboard's
    # leftmost and upmost pixels as well as the board's size
    if col_coords_are_found and row_coords_are_found:
        grid_square_size = chessboard_size / 8
        scaled_row_coords = [upmost_chessboard_pixel]
        scaled_col_coords = [leftmost_chessboard_pixel]
        for i in range(0, 8):
            scaled_row_coords.append(scaled_row_coords[-1] + grid_square_size)
            scaled_col_coords.append(scaled_col_coords[-1] + grid_square_size)
        scaled_row_coords = [round(row) for row in scaled_row_coords]
        scaled_col_coords = [round(col) for col in scaled_col_coords]
        
        # Scale the coordinates back up to the screen's actual resolution
        fullsize_row_coords = [(scaled_row_coord * SCREEN_HEIGHT) / SCALED_HEIGHT for scaled_row_coord in scaled_row_coords]
        fullsize_col_coords = [(scaled_col_coord * SCREEN_HEIGHT) / SCALED_HEIGHT for scaled_col_coord in scaled_col_coords]

        # Set return value
        board_coords = (fullsize_col_coords, fullsize_row_coords)
    else:
        print("chessboard not detected")
        board_coords = None

    return board_coords


# description  : Identify the chess piece at a given location on the board
# return       : ChessPiece
# precondition : get_board_coords() was executed and succesfully located the board,
#                col and row are integers
# postcondition: The ChessPiece object which corresponds to the specified location on
#                the board is returned. Note that an empty tile is a type of ChessPiece.
def identify_piece(col, row):
    global scaled_col_coords, scaled_row_coords, frame
    
    piece_name = 'unknown'
    tile_color = -1
    
    # Crop to piece location
    crop_x1 = scaled_col_coords[col-1]
    crop_x2 = scaled_col_coords[col]
    crop_y1 = scaled_row_coords[row-1]
    crop_y2 = scaled_row_coords[row]

    # Crop to square 
    crop_width  = crop_x2 - crop_x1
    crop_height = crop_y2 - crop_y1
    if crop_width > crop_height:
        crop_x1 += (crop_width - crop_height)
    elif crop_height > crop_width:
        crop_y1 += (crop_height - crop_width)

    # Get cropped image from current frame
    screen_piece_img = frame[crop_y1:crop_y2, crop_x1:crop_x2]

    # Scale the cropped image to match reference image dimension
    screen_piece_img = cv2.resize(screen_piece_img,
                                  dsize=(REFERENCE_IMG_DIM, REFERENCE_IMG_DIM),
                                  interpolation=cv2.INTER_CUBIC)

    # Set color of piece's tile
    if ((col + row) % 2 == 0):
        tile_color = 1 # white
    else:
        tile_color = 0 # black

    # Initialize variables for finding closest resemblence
    min_img_difference = _mse(screen_piece_img, CHESS_PIECES[0].img[tile_color])
    piece = CHESS_PIECES[0]
    
    # Loop through chess pieces
    for reference_piece in CHESS_PIECES:
        current_img_difference = _mse(screen_piece_img, reference_piece.img[tile_color])
        if current_img_difference < min_img_difference:
            min_img_difference = current_img_difference
            piece = reference_piece

    return piece


''' PRIVATE FUNCTIONS '''

# description  : Take a screenshot and optimize it for image recognition
# return       : 2D numpy array
# precondition : SCREEN_WIDTH and SCREEN_HEIGHT have been correctly initialized
# postcondition: a scaled down grayscale screenshot is returned
def _get_processed_screenshot():
    img = ImageGrab.grab(bbox=(0,0,SCREEN_WIDTH,SCREEN_HEIGHT))

    img = img.resize((
        round(SCALED_HEIGHT * SCREEN_RATIO), SCALED_HEIGHT))
    img_np = np.array(img)
    processed_screenshot = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    return processed_screenshot


# description  : Calculate the Mean Squared Error (mse) between two images.
#                The mse is the sum of the squared difference between the two
#                images. The smaller the error, the more similar the images.
# return       : float
# precondition : the two images must have the same dimension
# postcondition: the mse is returned
def _mse(imageA, imageB): 
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	return err


# description  : Cluster an array of objects based on a linked array of values
# return       : list of lists of objects
# precondition : object_array and value_array are linked (ie. value_array[3]
#                corresponds to a property of object_array[3])
# postcondition: The clustered lists of objects are returned
def _cluster_objects(object_array, value_array):

    # Compute KDE minima
    a = np.array(value_array).reshape(-1, 1)
    kde = KernelDensity(kernel='gaussian', bandwidth=1).fit(a)
    s = np.linspace(0, round(SCALED_HEIGHT/8), round(SCALED_HEIGHT/8))
    e = kde.score_samples(s.reshape(-1,1))
    minima = argrelextrema(e, np.less)[0]
    minima = np.append(minima, round(SCALED_HEIGHT/8) - 1)
    #debugging
    #print("Minima:", s[minima])

    # Generate array of 'minima' number of arrays
    clusters = []
    for minimum in minima:
        clusters.append([])

    # Break up original array of objects into clusters
    for object_index in range(0, len(object_array)):
        for minimum_index in range(0, len(minima)):
            if value_array[object_index] < minima[minimum_index]:
                clusters[minimum_index].append(object_array[object_index])
                break

    # Remove the smallest cluster (cpcs's of length 1 or 2)
    if len(clusters) > 0:
        clusters.pop(0)

    return clusters


# description  : Find a checker color pattern of length 8
# return       : integer
# precondition : cpcs_array is a list of cpcs's
# postcondition: If a checker pattern of length 8 is detected,
#                return the index at which the pattern begins,
#                Else, return -1
def _find_cpcs_checker_pattern(cpcs_array):
    i = 0
    pattern_start_index = 0
    checker_pattern_is_found = False
    while i < len(cpcs_array) and not checker_pattern_is_found:
        if i == 0:
            colorA = cpcs_array[i].color
        elif i == 1:
            colorB = colorA
            colorA = cpcs_array[i].color
            checker_pattern_counter = 2
        else:
            if cpcs_array[i].color == colorB and colorA != colorB:
                checker_pattern_counter += 1
                if checker_pattern_counter == 8:
                    checker_pattern_is_found = True
            else:
                checker_pattern_counter = 2
                pattern_start_index = i - 1
            colorB = colorA
            colorA = cpcs_array[i].color
        i += 1
    
    if not checker_pattern_is_found:
        pattern_start_index = -1
    
    return pattern_start_index
