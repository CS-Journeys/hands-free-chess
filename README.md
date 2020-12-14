# Hands-Free Chess
Play chess online using only your voice instead of a keyboard and mouse!

## Getting started
1. Install [Python 3.6.8](https://www.python.org/downloads/) (version 3.6 is required for using the SpeechRecognition library)
2. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies

```pip install -r requirements.txt```

(Installing in a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) is highly recommended)

## Usage
1. Begin chess game on [chess.com](https://www.chess.com)
2. Set board coordinates to "outside" instead of "inside" (chess.com > Settings > Coordinates)
3. Run ```py main.py``` or ```python main.py``` via the command line
4. Say a single or combination of [keywords](res/keywords.txt)

Let the program do the rest!

To exit, press ```CTRL + C``` in the command line or say "exit" into the mic.
