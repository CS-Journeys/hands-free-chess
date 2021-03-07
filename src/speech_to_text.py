"""
Hands-Free Chess allows the user to play chess online using only their voice instead of a keyboard and mouse.
Copyright (C) 2020-2021  CS Journeys

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import speech_recognition as sr
import logging

PAUSE_THRESHOLD = 0.5 # TODO: experiment with this value
NOISE_SAMPLE_DURATION = 1.0 # the sample duration for estimating the ambient noise


class SpeechRecognizer:
    NOT_RECOGNIZED = "-1"

    """ CONSTRUCTOR """
    def __init__(self, raw_text_queue):
        self.log = logging.getLogger("src.command_recognition")

        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = PAUSE_THRESHOLD
        self.mic = sr.Microphone()

        self.raw_text_queue = raw_text_queue
        self.stop_listening = None # call this function to clean up the speech recognizer

        # Adjust the microphone for ambient noise
        self.log.info("Gathering audio data to adjust for ambient noise")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, NOISE_SAMPLE_DURATION)
        self.log.info("Ambient noise adjustments complete")

    """ PUBLIC """
    def listen_in_background(self):
        self.stop_listening = self.recognizer.listen_in_background(self.mic, self._recognize_command)
        self.log.info("Listening in background...")

    """ PRIVATE """
    def _recognize_command(self, recognizer, audio):
        try:
            raw_text = recognizer.recognize_google(audio)
            self.raw_text_queue.put(raw_text)
            self.log.info(f"Put \"{raw_text}\" into the raw text queue")
        except sr.UnknownValueError:
            self.log.warning("Google Speech Recognition could not understand audio")
            self.raw_text_queue.put(self.NOT_RECOGNIZED)
        except sr.RequestError as e:
            self.log.error(f"Could not request results from Google Speech Recognition service; {e}")
