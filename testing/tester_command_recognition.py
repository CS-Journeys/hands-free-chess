import sys
sys.path.append("../")
from src.command_recognition import *

user_command = []

adjust_for_ambient_noise(2.0)
while user_command != ['exit']:
    user_command = get_voice_command()
