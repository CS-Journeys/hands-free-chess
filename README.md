# Hands-Free Chess
Play chess online using only your voice instead of a keyboard and mouse!

## Getting started
1. Install [Python 3.6](https://www.python.org/downloads/release/python-368/) (version 3.6 is required for using the SpeechRecognition library)
2. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies

```pip install -r requirements.txt```

(Installing in a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) is highly recommended)

## Usage
1. Login/sign up to [chess.com](https://www.chess.com)
2. Set board coordinates to "outside" instead of "inside" (chess.com > Settings > Board and Pieces > Coordinates)
3. Begin chess game
4. Run ```py app.py``` or ```python app.py``` via the command line
5. Make chessboard as big as possible to increase image recognition reliability
5. Say a single or combination of [keywords](res/keywords.txt)

Let the program do the rest!

To exit, press ```CTRL + C``` in the command line or say "exit" into the mic.

## License
[GPL](LICENSE)
