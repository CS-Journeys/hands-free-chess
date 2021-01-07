# Hands-Free Chess
Play chess online using only your voice instead of a keyboard and mouse!

## Getting started
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

## Usage
1. Run `python app.py` or, on linux `python3 app.py` via the command line  
2. Follow the instructions from the "Help" button
 
## License
[GPL](LICENSE)
