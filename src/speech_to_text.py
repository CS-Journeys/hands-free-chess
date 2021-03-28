import speech_recognition as sr
import logging

PAUSE_THRESHOLD = 0.5 # TODO: experiment with this value
NOISE_SAMPLE_DURATION = 1.0 # the sample duration for estimating the ambient noise


class SpeechRecognizer:
    """
    The SpeechRecognizer class listens to the user's microphone and uses the Google speech recognition API to
    transcribe every word spoken by the user.
    """

    # TODO: use an actual exception
    # A special value, used like an exception, for whenever the Speech Recognizer "hears" audio,
    # but doesn't recognize it
    NOT_RECOGNIZED = "-1"

    ''' CONSTRUCTOR '''
    def __init__(self, raw_text_queue):
        self.log = logging.getLogger(__name__)

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

    ''' PUBLIC '''
    def listen_in_background(self):
        """
        Listen for audio by activating the microphone, then call a callback function to handle a chunk of audio that is
        louder than a certain threshold.
        Runs on a separate thread. Listens infinitely, until stop_listening() is called.
        """
        self.stop_listening = self.recognizer.listen_in_background(self.mic, self._recognize_audio)
        self.log.info("Listening in background...")

    ''' PRIVATE '''
    def _recognize_audio(self, recognizer, audio):
        """
        This function attempts to transcribe a chunk of audio. The function is called whenever
        listen_in_background() detects noise.

        Parameters:
            - recognizer: a Recognizer() object from the SpeechRecognition library (imported as sr), transcribe
                the audio.
            - audio: an AudioData instance that represents the chunk of audio to be transcribed
        Output:
            - return: none
            - queue: the transcribed text is put in a queue to be processed by another thread
        """
        try:
            raw_text = recognizer.recognize_google(audio)
            self.raw_text_queue.put(raw_text)
            self.log.info(f"Put \"{raw_text}\" into the raw text queue")
        except sr.UnknownValueError:
            self.log.warning("Google Speech Recognition could not understand audio")
            self.raw_text_queue.put(self.NOT_RECOGNIZED)
        except sr.RequestError as e:
            self.log.error(f"Could not request results from Google Speech Recognition service; {e}")
