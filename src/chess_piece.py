import numpy as np
from PIL import Image

IMG_FILEPATH = 'res/chess-piece-images/'

class ChessPiece:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.img_onblack_fname = name + '-' + color + '-black.png'
        self.img_onwhite_fname = name + '-' + color + '-white.png'
        self.img = [np.array(Image.open(IMG_FILEPATH + self.img_onblack_fname)),
                    np.array(Image.open(IMG_FILEPATH + self.img_onwhite_fname))]
