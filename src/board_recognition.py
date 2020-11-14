from PIL import ImageGrab
import numpy as np
import cv2
import tkinter

from src import chess_piece

tkinter_root  = tkinter.Tk()
SCREEN_WIDTH  = tkinter_root.winfo_screenwidth()
SCREEN_HEIGHT = tkinter_root.winfo_screenheight()
tkinter_root.destroy()
SCREEN_RATIO  = SCREEN_WIDTH / SCREEN_HEIGHT
SCREEN_SCALAR = 400
REFERENCE_IMG_DIM = 33 # width and height in pixels

scaled_col_coords = []
scaled_row_coords = []
frame = None

chess_pieces = [chess_piece.ChessPiece('pawn', 'black'),
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

def get_processed_screenshot():
    img = ImageGrab.grab(bbox=(0,0,SCREEN_WIDTH,SCREEN_HEIGHT))

    img = img.resize((
        int(SCREEN_SCALAR * SCREEN_RATIO), SCREEN_SCALAR))
    img_np = np.array(img)
    processed_screenshot = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    return processed_screenshot

def get_board_coords():
    global scaled_col_coords, scaled_row_coords, frame

    scaled_row_coords = []
    frame = get_processed_screenshot()

    columnsNotDetected = True
    pixelRow = int(SCREEN_SCALAR / 4) # don't start scanning at 0th pixel to save time
    while (columnsNotDetected and pixelRow < SCREEN_SCALAR):
        scaled_col_coords = []

        # Scan single pixel row for column pattern
        previousPixel = -1
        samePixelCount = 1
        continuous_pixel_series = []
        new_pixel_index = -1
        for i, pixel in enumerate(frame[pixelRow]):
            if previousPixel - 10 <= pixel <= previousPixel + 10:
                samePixelCount += 1
            else:
                if (samePixelCount > 3):
                    continuous_pixel_series.append(
                        (new_pixel_index, samePixelCount))
                new_pixel_index = i
                samePixelCount = 1
            previousPixel = pixel

        # Select the 8 column coordinates
        grid_width = -1
        for i, item in enumerate(continuous_pixel_series):
            if (continuous_pixel_series[i-1][1] - 1 <= continuous_pixel_series[i][1] and
                continuous_pixel_series[i][1] <= continuous_pixel_series[i-1][1] + 1):

                current_width = continuous_pixel_series[i][0] - continuous_pixel_series[i-1][0]
                if (grid_width == -1):
                    grid_width = current_width
                if len(scaled_col_coords) < 8 and grid_width - 1 <= current_width and current_width <= grid_width + 1:
                    scaled_col_coords.append(continuous_pixel_series[i][0] - 1)

        # Insert board's horizontal bounding coords if possible
        if (len(scaled_col_coords) == 7):
            scaled_col_coords.insert(0, scaled_col_coords[0] - grid_width)
            scaled_col_coords.append(scaled_col_coords[len(scaled_col_coords) - 1] + grid_width)
            columnsNotDetected = False

        pixelRow += 1

    if (pixelRow >= SCREEN_SCALAR):
        print("chessboard columns not detected")
        return None


    print(scaled_col_coords)

    # Scan single pixel column for row pattern
    previousPixel = -1
    samePixelCount = 1
    continuous_pixel_series = []
    new_pixel_index = -1
    
    for i, pixel in enumerate(frame[:,scaled_col_coords[0] + 1]):
        if previousPixel - 10 <= pixel <= previousPixel + 10:
            samePixelCount += 1
        else:
            if (samePixelCount > 3):
                continuous_pixel_series.append(
                    (new_pixel_index, samePixelCount))
            new_pixel_index = i
            samePixelCount = 1
        previousPixel = pixel

    # Select the 8 row coordinates
    grid_height = -1
    for i, item in enumerate(continuous_pixel_series):
        if (continuous_pixel_series[i-1][1] - 1 <= continuous_pixel_series[i][1] and
            continuous_pixel_series[i][1] <= continuous_pixel_series[i-1][1] + 1):
            current_height = continuous_pixel_series[i][0] - continuous_pixel_series[i-1][0]
            if (grid_height == -1):
                if (continuous_pixel_series[i][1] - 1 <= continuous_pixel_series[i+1][1] and
                    continuous_pixel_series[i+1][1] <= continuous_pixel_series[i][1] + 1):
                    grid_height = current_height
            if len(scaled_row_coords) < 8 and grid_height - 1 <= current_height and current_height <= grid_height + 1:
                scaled_row_coords.append(continuous_pixel_series[i][0] - 1)

    # Insert board's vertical bounding coords if possible
    if (len(scaled_row_coords) == 7):
        scaled_row_coords.insert(0, scaled_row_coords[0] - grid_height)
        scaled_row_coords.append(scaled_row_coords[len(scaled_row_coords) - 1] + grid_height)
    else:
        print("chessboard rows not detected")
        return None

    fullsize_row_coords = [(scaled_row_coord * SCREEN_HEIGHT) / SCREEN_SCALAR for scaled_row_coord in scaled_row_coords]
    fullsize_col_coords = [(scaled_col_coord * SCREEN_HEIGHT) / SCREEN_SCALAR for scaled_col_coord in scaled_col_coords]

    return fullsize_col_coords, fullsize_row_coords

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def identify_piece(col, row):
    piece_name = 'unknown'
    tile_color = -1
    
    # Crop to piece location
    crop_x1 = scaled_col_coords[col-1]
    crop_x2 = scaled_col_coords[col] + 1
    crop_y1 = scaled_row_coords[row-1]
    crop_y2 = scaled_row_coords[row] + 1

    # Crop to square 
    crop_width  = crop_x2 - crop_x1
    crop_height = crop_y2 - crop_y1
    if crop_width > crop_height:
        crop_x1 += int((crop_width - crop_height) / 2)
        crop_x2 -= int((crop_width - crop_height) / 2)
    elif crop_height > crop_width:
        crop_y1 += int((crop_height - crop_width) / 2)
        crop_y2 -= int((crop_height - crop_width) / 2)

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
    min_img_difference = mse(screen_piece_img, chess_pieces[0].img[tile_color])
    piece_name = chess_pieces[0].name
    
    # Loop through chess pieces
    for reference_piece in chess_pieces:
        current_img_difference = mse(screen_piece_img, reference_piece.img[tile_color])
        if current_img_difference < min_img_difference:
            min_img_difference = current_img_difference
            piece_name = reference_piece.name

    return piece_name
