import logging
import time
from PIL import ImageGrab
import numpy as np
import cv2
import pyautogui
import queue
from sklearn.neighbors import KernelDensity
from scipy.signal import argrelextrema
from src.chess_piece import ChessPiece


''' CUSTOM DATA TYPES '''
class ConsecutivePixelColorSequence:
    """
    Each cpcs has a color, start index, and length.
    """
    def __init__(self, color, start_pixel, length=1):
        self.color = color
        self.start_pixel = start_pixel
        self.length = length


''' CONSTANTS '''
SCALED_HEIGHT = 720 # arbitrary low resolution to reduce computation time
REFERENCE_IMG_DIM = 33 # width and height in pixels
CHESS_PIECES = [ChessPiece('pawn', 'black'),
                ChessPiece('rook', 'black'),
                ChessPiece('knight', 'black'),
                ChessPiece('bishop', 'black'),
                ChessPiece('queen', 'black'),
                ChessPiece('king', 'black'),
                ChessPiece('pawn', 'white'),
                ChessPiece('rook', 'white'),
                ChessPiece('knight', 'white'),
                ChessPiece('bishop', 'white'),
                ChessPiece('queen', 'white'),
                ChessPiece('king', 'white'),
                ChessPiece('empty', 'empty')]
EMPTY_RECOGNITION_THRESHOLD = 1000


class BoardRecognizer:
    """
    The BoardRecognizer class handles the required image recognition for locating the board on the screen and
    determining the board's state (i.e., the location of each piece on the board).

    Note that the current board recognition only supports the default chess.com chessboard style. Even then,
    the image recognition is finicky. A better solution might be to use machine/deep learning for the image recognition.
    """

    ''' CONSTRUCTOR '''
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.screen_width = pyautogui.size()[0]
        self.screen_height = pyautogui.size()[1]
        self.log.debug("Screen size: {" + f"width: {self.screen_width}, height: {self.screen_height}" + "}")
        self.frame = None
        self.scaled_col_coords = []
        self.scaled_row_coords = []

    ''' PUBLIC FUNCTIONS '''
    def endlessly_recognize_board(self, board_queue, pause_time, stop_event):
        """
        This function repeatedly recognizes the board until it is told to stop by the stop_event.

        Parameters:
            - board_queue: a queue in which to store the board's coordinates and state (i.e. location of each piece)
            - pause_time: the amount of time (in seconds) to pause before running the board recognition algorithm again
            - stop_event: a threading event that, when set, causes the function to stop
        Output:
            - return: none
            - queue: the boards coordinates and state are stored in the board_queue as a two-element tuple
                the first element is an array of values representing the x and y coordinates of each line on the board
                the second element is a 8x8 NumPy array representing the board state (i.e. the location of each piece)
        """
        self.log.debug("Beginning endless loop of board recognition...")
        while not stop_event.is_set():
            self.recognize_board(board_queue)
            time.sleep(pause_time)

    def recognize_board(self, board_queue):
        """
        This function finds the coordinates of each of the board's gridlines and the location of each piece on the board

        Parameters:
            - board_queue: the queue in which to store the board's coordinates and state (i.e. location of each piece)
        Output:
            - return: none
            - queue: the boards coordinates and state are stored in the board_queue as a two-element tuple
                the first element is an array of values representing the x and y coordinates of each line on the board
                the second element is a 8x8 NumPy array representing the board state (i.e. the location of each piece)
        """
        board_coords = self._get_board_coords()
        if board_coords is not None:
            # TODO: properly initialize the numpy array
            board_state = np.full((8, 8), ChessPiece('unknown', 'unknown'))
            for row in range(1, 8 + 1):
                for col in range(1, 8 + 1):
                    board_state[row - 1][col - 1] = self._identify_piece(col, row)
            try:
                board_queue.put_nowait((board_coords, board_state))
            except queue.Full:
                board_queue.get()
                board_queue.put((board_coords, board_state))

    ''' PRIVATE FUNCTIONS '''
    def _get_board_coords(self):
        """
        This function finds the chessboard and its coordinates on the screen. It locates the chessboard by
        searching for the checker pattern.

        Parameters:
            - none
        Output:
            - return: if the chessboard is detected, return a tuple of two lists of floats --
                        the first list contains the x pixel coordinates of each vertical line,
                        and the second list contains the y pixel coordinates of each horizontal line
                      if the chessboard is not detected, return None
        """
        # Take screenshot
        self.frame = self._get_processed_screenshot()
        ss_width = self.frame.shape[1]  # ss is short for screenshot
        ss_height = self.frame.shape[0]

        # Reset coordinates
        self.scaled_row_coords = []
        self.scaled_col_coords = []

        # FIND COLUMN COORDINATES
        col_coords_are_found = False
        i = round(ss_height / 4)
        while i < round((3 / 4) * ss_height) and not col_coords_are_found:
            # Split row into consecutive pixel color sequences
            consecutive_color_arr = [ConsecutivePixelColorSequence(self.frame[i, 0], 0)]
            for j in range(1, ss_width):
                if self.frame[i, j] == consecutive_color_arr[-1].color:
                    consecutive_color_arr[-1].length += 1
                else:
                    consecutive_color_arr.append(ConsecutivePixelColorSequence(self.frame[i, j], j))

            # 'cpcs' stands for 'ConsecutivePixelColorSequence'
            # Cluster the cpcs's by length
            consecutive_color_arr_lengths = [sequence.length for sequence in consecutive_color_arr]
            cpcs_length_clusters = self._cluster_objects(consecutive_color_arr, consecutive_color_arr_lengths)

            # Find checker pattern
            for cluster in cpcs_length_clusters:
                checker_pattern_start_index = self._find_cpcs_checker_pattern(cluster)
                if checker_pattern_start_index != -1:
                    col_coords_are_found = True

                    # Set chessboard column pixel start
                    first_cpcs = cluster[checker_pattern_start_index]
                    actual_first_square_length = \
                        cluster[checker_pattern_start_index + 1].start_pixel - first_cpcs.start_pixel
                    pixel_offset = (actual_first_square_length - first_cpcs.length) / 2
                    leftmost_chessboard_pixel = first_cpcs.start_pixel - pixel_offset

                    # Set chessboard size
                    chessboard_size = cluster[checker_pattern_start_index + 7].start_pixel - cluster[
                        checker_pattern_start_index].start_pixel
                    chessboard_size = chessboard_size + (chessboard_size / 7) + 1

                    chessboard_size -= 2
                    break

            i += 1

        # FIND ROW COORDINATES
        if col_coords_are_found:
            row_coords_are_found = False
            i = round(leftmost_chessboard_pixel)
            while i < ss_width and not row_coords_are_found:
                # Split column into consecutive pixel color sequences
                consecutive_color_arr = [ConsecutivePixelColorSequence(self.frame[0, i], 0)]
                for j in range(1, ss_height):
                    if self.frame[j, i] == consecutive_color_arr[-1].color:
                        consecutive_color_arr[-1].length += 1
                    else:
                        consecutive_color_arr.append(ConsecutivePixelColorSequence(self.frame[j, i], j))

                # 'cpcs' stands for 'ConsecutivePixelColorSequence'
                # Cluster the cpcs's by length
                consecutive_color_arr_lengths = [sequence.length for sequence in consecutive_color_arr]
                cpcs_length_clusters = self._cluster_objects(consecutive_color_arr, consecutive_color_arr_lengths)

                # Find checker pattern
                for cluster in cpcs_length_clusters:
                    checker_pattern_start_index = self._find_cpcs_checker_pattern(cluster)
                    if checker_pattern_start_index != -1:
                        row_coords_are_found = True

                        # Set chessboard row pixel start
                        first_cpcs = cluster[checker_pattern_start_index]
                        actual_first_square_length = \
                            cluster[checker_pattern_start_index + 1].start_pixel - first_cpcs.start_pixel
                        pixel_offset = (actual_first_square_length - first_cpcs.length) / 2
                        upmost_chessboard_pixel = first_cpcs.start_pixel - pixel_offset

                        break

                i += 1

        # Set the coordinates of every grid line based on the chessboard's
        # leftmost and upmost pixels as well as the board's size
        if col_coords_are_found and row_coords_are_found:
            grid_square_size = chessboard_size / 8
            self.scaled_row_coords = [upmost_chessboard_pixel]
            self.scaled_col_coords = [leftmost_chessboard_pixel]
            for i in range(0, 8):
                self.scaled_row_coords.append(self.scaled_row_coords[-1] + grid_square_size)
                self.scaled_col_coords.append(self.scaled_col_coords[-1] + grid_square_size)
            self.scaled_row_coords = [round(row) for row in self.scaled_row_coords]
            self.scaled_col_coords = [round(col) for col in self.scaled_col_coords]

            # Scale the coordinates back up to the screen's actual resolution
            fullsize_row_coords = [(scaled_row_coord * self.screen_height) / SCALED_HEIGHT for scaled_row_coord in
                                   self.scaled_row_coords]
            fullsize_col_coords = [(scaled_col_coord * self.screen_height) / SCALED_HEIGHT for scaled_col_coord in
                                   self.scaled_col_coords]

            # Set return value
            board_coords = (fullsize_col_coords, fullsize_row_coords)
        else:
            board_coords = None

        return board_coords

    def _identify_piece(self, col, row):
        """
        This function identifies the chess piece at a given location on the board. It uses the Mean Squared Error (mse)
        to check which chess piece reference image is most similar to the image of the given location on the board.
        The function returns the piece type that the most similar reference image represents.

        Pre-condition:
            - _get_board_coords() must have successfully located the board's coordinates
        Parameters:
            - col: an integer (0-7) that represents the column of the piece to be identified
            - row: an integer (0-7) that represents the row of the piece to be identified
        Output:
            - return: the ChessPiece object which represents the piece at the given location. Note that
                an empty tile is a type of ChessPiece
        """
        # Crop to piece location
        crop_x1 = self.scaled_col_coords[col-1]
        crop_x2 = self.scaled_col_coords[col]
        crop_y1 = self.scaled_row_coords[row-1]
        crop_y2 = self.scaled_row_coords[row]

        # Crop to square
        crop_width = crop_x2 - crop_x1
        crop_height = crop_y2 - crop_y1
        if crop_width > crop_height:
            crop_x1 += (crop_width - crop_height)
        elif crop_height > crop_width:
            crop_y1 += (crop_height - crop_width)

        # Get cropped image from current frame
        screen_piece_img = self.frame[crop_y1:crop_y2, crop_x1:crop_x2]

        # Scale the cropped image to match reference image dimension
        screen_piece_img = cv2.resize(screen_piece_img,
                                      dsize=(REFERENCE_IMG_DIM, REFERENCE_IMG_DIM),
                                      interpolation=cv2.INTER_CUBIC)

        # Set color of piece's tile
        if (col + row) % 2 == 0:
            tile_color = 1 # white
        else:
            tile_color = 0 # black

        # Initialize variables for finding closest resemblance
        min_img_difference = self._mse(screen_piece_img, CHESS_PIECES[0].img[tile_color])
        piece = CHESS_PIECES[0]

        # Loop through chess pieces
        for reference_piece in CHESS_PIECES:
            current_img_difference = self._mse(screen_piece_img, reference_piece.img[tile_color])
            if current_img_difference < min_img_difference:
                if not (reference_piece.name == 'empty' and current_img_difference > EMPTY_RECOGNITION_THRESHOLD):
                    min_img_difference = current_img_difference
                    piece = reference_piece

        return piece

    def _get_processed_screenshot(self):
        """
        This function takes a screenshot and optimizes it for image recognition 
        (i.e. scale and reduce to monochromatic)

        Parameters: none
        Output:
            - return: a two dimensional NumPy array that represents the scaled down screenshot
        """
        # Take screenshot
        img = ImageGrab.grab()

        # Process screenshot
        img = img.resize((
            round(SCALED_HEIGHT * self.screen_width / self.screen_height), SCALED_HEIGHT))
        img_np = np.array(img)
        processed_screenshot = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        return processed_screenshot

    @staticmethod
    def _cluster_objects(object_array, value_array):
        """
        This function clusters an array of objects based on a linked array of values.
        Uses Kernel Density Estimation (KDE) clustering.

        Parameters:
            - object_array: a list of objects to be clustered by their associated values
            - value_array: the list of values to which each object is associated
        Output:
            - return: a list of lists of objects, where each sub-list represents a cluster
        """
        # Compute KDE minima
        a = np.array(value_array).reshape(-1, 1)
        kde = KernelDensity(kernel='gaussian', bandwidth=1).fit(a)
        s = np.linspace(0, round(SCALED_HEIGHT/8), round(SCALED_HEIGHT/8))
        e = kde.score_samples(s.reshape(-1,1))
        minima = argrelextrema(e, np.less)[0]
        minima = np.append(minima, round(SCALED_HEIGHT/8) - 1)

        # Generate array of 'minima' number of arrays
        clusters = []
        for _ in minima:
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

    @staticmethod
    def _find_cpcs_checker_pattern(cpcs_array):
        """
        This function finds an alternating color pattern of length 8.

        Parameters:
            - cpcs_array: an array of ConsecutivePixelColorSequences (cpcs)
        Output:
            - return: the index of the cpcs in the cpcs_array at which an alternating pattern of length 8 begins
                return -1 if no pattern is found
        """
        i = 0
        pattern_start_index = 0
        checker_pattern_is_found = False
        while i < len(cpcs_array) and not checker_pattern_is_found:
            if i == 0:
                color_a = cpcs_array[i].color
            elif i == 1:
                color_b = color_a
                color_a = cpcs_array[i].color
                checker_pattern_counter = 2
            else:
                if cpcs_array[i].color == color_b and color_a != color_b:
                    checker_pattern_counter += 1
                    if checker_pattern_counter == 8:
                        checker_pattern_is_found = True
                else:
                    checker_pattern_counter = 2
                    pattern_start_index = i - 1
                color_b = color_a
                color_a = cpcs_array[i].color
            i += 1

        if not checker_pattern_is_found:
            pattern_start_index = -1

        return pattern_start_index

    @staticmethod
    def _mse(image_a, image_b):
        """
        This function calculates the Mean Squared Error (mse) between two images. The mse is the sum of the squared
        difference of between each pixel of the two images. The smaller the error, the more similar the images.

        Parameters:
            - image_a: a NumPy array that represents one of the two images to be compared
            - image_b: a NumPy array of the same dimension as image_a and represents the other image to be compared
        Output:
            - return: a float that represents the mse between the two images
        """
        err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
        err /= float(image_a.shape[0] * image_a.shape[1])
        return err
