# Hands-Free Chess
Play chess online using only your voice instead of a keyboard and mouse!

## Download
You can [download](https://github.com/CS-Journeys/hands-free-chess/releases/tag/v1.0.0) the latest version of Hands-Free Chess for Windows, Mac OS, and Linux.

## Installation (for developers)
### Windows
1. Install [Python 3.6](https://www.python.org/downloads/release/python-368/) (version 3.6 is required for using the SpeechRecognition library)
2. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies  
```pip install -r requirements.txt```  
(Installing in a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) is highly recommended)

### MacOS
1. Install [Python 3.6](https://www.python.org/downloads/release/python-368/) (version 3.6 is required for using the SpeechRecognition library)
2. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies  
```pip install -r requirements.txt```  
(Installing in a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) is highly recommended)
3. Mac Users:  
    a. Open System Preferences  
    b. Navigate to Security & Privacy > Screen Recording  
    c. Click the lock icon to make a change  
    d. Make sure your python IDE (PyCharm, Idle, etc.) or the `Terminal` is checked off. This allows the application to monitor your screen while you play so it can recognize the board and pieces.
    
### Linux (Debian/Ubuntu)
1. Install Python 3.6 (check to see if 3.6 is pre-installed on your system, and if not, use your package manager)
2. Install required linux packages  
```sudo apt-get install portaudio19-dev python-all-dev python3-tk python3-dev python3-venv python3-pip```
3. Update pip  
```pip3 install --upgrade pip```
4. Use pip to install python dependencies  
```pip3 install -r requirements.txt```  
(Installing in a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) is highly recommended)

## Contributing
CS Journeys welcomes contributions to [our open source projects on Github](https://github.com/CS-Journeys). All contributions, regardless of your skill level, are appreciated!

### Issues
If PyAudio is not properly installing, you may need to either downgrade your Python version to 3.6 or install the pipwin library.

Feel free to submit issues and enhancement requests.

### Developing
You can solve issues or be creative and add features that you think would improve HFC. Please try to follow the project's coding style.

## License
[GPL](LICENSE)
