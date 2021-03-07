import sys
import queue
import time
sys.path.append("../")
from src.speech_to_text import CommandRecognizer
from src.log_manager import LogManager

log_manager = LogManager()

cmd_queue = queue.Queue()
cmd_recog = CommandRecognizer(cmd_queue)

cmd_recog.listen_in_background()

# do some unrelated things for 10 seconds
for i in range(100):
    time.sleep(0.1)

while not cmd_queue.empty():
    print(cmd_queue.get())

cmd_recog.stop_listening()
