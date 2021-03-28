"""
This class handles the following process:
text -> words -> commands
"""
import yaml
import logging
from src.command import Command
from src.command import MoveCommand

COMMAND_DICTIONARY_FILE = 'res/speech-to-command/command_dictionary.yaml'
MISINTERPRETATIONS_FILE = 'res/speech-to-command/misinterpretations.txt'


class TextToCmdBuffer:
    """
    The TextToCmdBuffer class converts raw text from the SpeechRecognizer class into Command and MoveCommand objects.
    As raw text is progressively added to the buffer, the TextToCmdBuffer processes the raw text.
    The ControllerThread (see game_controller.py) extracts commands from the buffer as soon as they are complete.
    """

    ''' CONSTRUCTOR '''
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.words = []

        # Load keywords and command formats from a file
        self.command_formats = []
        self.keywords_dictionary = {}
        with open(COMMAND_DICTIONARY_FILE) as cmd_dict_file:
            cmd_dictionary = yaml.safe_load(cmd_dict_file)
            for key, value in cmd_dictionary.items():
                if key == 'keywords':
                    self.keywords_dictionary = value
            for key, value in cmd_dictionary.items():
                if key == 'command_formats':
                    for format_type, command_type in value.items():
                        self.command_formats.append(CommandFormat(format_type, command_type))

        self.start_cmd_words = self.keywords_dictionary['single_command_words'].copy()
        self.start_move_words = self.keywords_dictionary['start_move_words'].copy()
        self.start_cmd_words.extend(self.start_move_words)

        # Load a list of common misinterpretations from a file
        self.misinterpretations = []
        with open(MISINTERPRETATIONS_FILE, 'r') as mis_file:
            for cnt, line in enumerate(mis_file):
                actual, expected = line.split(',')
                expected = expected.rstrip('\n')
                self.misinterpretations.append(Misinterpretation(actual, expected))

    ''' PUBLIC FUNCTIONS '''
    def add_text(self, raw_text):
        """
        Convert raw text into a list of new words and update the word buffer accordingly.

        All new words that precede a "start command" word are discarded (if the word buffer is empty),
        and all new words that precede the word "cancel" are discard. The word buffer is emptied if a new command is
        being started. Otherwise, the new words are simply appended to the word buffer.

        Parameters:
            - raw_text: a string
        Return:
            - the list of words in the updated word buffer
        """
        self.log.debug(f"Before text addition: {self.words}")

        # Make the text lowercase
        lower_text = raw_text.lower()

        # Fix misinterpretations that the Speech Recognizer commonly makes
        reinterpreted_text = self._fix_misinterpretations(lower_text)

        # Split up the single string into multiple words
        new_words = self._split_into_words(reinterpreted_text)

        # Discard all new words that precede a "start command" word (if the old word buffer is empty)
        # and discard all new words that precede the word "cancel"
        for i, word in reversed(list(enumerate(new_words))):
            if word in self.start_cmd_words and len(self.words) == 0:
                new_words = new_words[i:]
            if word == "cancel":
                if len(new_words) > i + 1:
                    new_words = new_words[i+1:]

        # Empty the old word buffer if the first new word is a "start command" word
        if new_words[0] in self.start_cmd_words:
            self.clear()

        # Add the new words to the word buffer
        self.words.extend(new_words)

        # Empty the word buffer if it doesn't start with a "start command" word
        if self.words[0] not in self.start_cmd_words:
            self.clear()

        self.log.debug(f"After text addition: {self.words}")

        return self.words

    def get_command(self):
        """
        Extract a command from the buffer, if the buffer contains is a sequence of words that represents a command.
        Otherwise, return None.

        Pre-condition:
            - the first element of the word buffer is a "start command" word (or the word buffer is empty)
        Parameters:
            - none
        Return:
            - command: a move command (ie. Move object), a normal command (ie. Command object), or None
        """
        command = None
        word_ndx = 0
        possible_formats = self.command_formats.copy()

        self.log.debug(f"Before command extraction: {self.words}")

        # Check to see if the sequence of the first 'word_ndx' number of words matches a command format
        while word_ndx < len(self.words) and len(possible_formats) > 0:
            format_ndx = 0

            # Loop through every possible format
            while format_ndx < len(possible_formats):
                possible_format = possible_formats[format_ndx]

                if self.words[word_ndx] in self.keywords_dictionary[possible_format.get_word_type(word_ndx)]:
                    # Fix the 2/to misinterpretation
                    if self.words[word_ndx] == '2' and possible_format.get_word_type(word_ndx) == 'to':
                        self.words[word_ndx] = 'to'

                    # If the first 'word_ndx' number of words matches a command format,
                    # set the return value to the command that the first 'word_ndx' number of words represents
                    if possible_format.length == word_ndx + 1:
                        if possible_format.name.find('move') != -1:
                            command = MoveCommand(self.words[:word_ndx + 1])
                        elif possible_format.name.find('single') != -1:
                            command = Command(self.words[:word_ndx + 1])
                        possible_formats.pop(format_ndx)
                    else:
                        format_ndx += 1

                # Remove all invalid formats
                else:
                    possible_formats.pop(format_ndx)
            word_ndx += 1

        if command is not None:
            del self.words[:command.length]

        self.log.debug(f"After extraction: {self.words}")

        return command

    def clear(self):
        """
        Clear the TextToCmdBuffer of every word.
        """
        self.words = []

    ''' PRIVATE FUNCTIONS '''
    def _fix_misinterpretations(self, text):
        """
        Fix commonly misinterpreted words.

        Parameters:
            - text: a lowercase string to be reinterpreted
        Return:
            - the string with corrected misinterpretations
        """
        self.log.debug(f"Text (with misinterpretations): {text}")
        fixed_text = text
        for misinterpretation in self.misinterpretations:
            fixed_text = fixed_text.replace(misinterpretation.actual, misinterpretation.expected)
        self.log.debug(f"Text (without misinterpretations): {fixed_text}")
        return fixed_text

    @staticmethod
    def _split_into_words(text):
        """
        Splits a string into an list of strings, called "words."
        Note that words are not merely delimited by whitespace: alpha and numeric
        characters must be separated into words.

        Parameters:
            - text: the string to be split
        Return:
            - words: the list of words which result from splitting the input string
        Example:
            _split_into_words("My knight E5 to WOW!")
            ===> returns ["My", "knight", "E", "5", "to", "WOW!"]
        """
        words = []
        temp_alpha = ""

        # Split string into words
        for char in text:
            if char.isdigit():
                words.append(temp_alpha)
                temp_alpha = ""
                words.append(char)
            elif char == ' ':
                words.append(temp_alpha)
                temp_alpha = ""
            else:
                temp_alpha += char
        words.append(temp_alpha)

        # Remove empty words
        for i, part in enumerate(words):
            if part == '':
                words.remove(part)

        return words


class CommandFormat:
    """
    HFC supports a variety of command formats (single-word commands like "cancel," move commands like "knight e5" or
    "king g5 to g6," etc.)
    A CommandFormat object stores:
        (a) The format's name ("implicit_destination_move," "single_word_command," etc.)
        (b) A list of strings that represents the format's component types
            (ex: ["start_move_words", "to", "letter_words", "digit_words"])
        (c) The length of the format (i.e., the number of words or "components" in the format)
    """
    def __init__(self, name, components):
        self.name = name
        self.components = components
        self.length = len(components)

    def get_word_type(self, ndx):
        """
        This function returns the type of word/component that occurs at the specified index.

        Parameters:
            - ndx: the index of the component whose type is to be returned
        Return:
            - The string representation of the type of word at the specified index.
                If there are no words at the specified index, return an empty string.
        Example:
            components: ["start_move_words", "to", "letter_words", "digit_words"]
            get_word_type(2) --> returns "letter_words"
        """
        if ndx < self.length:
            return self.components[ndx]
        else:
            return ""


class Misinterpretation:
    """
    For every common misinterpretation, there is
        (a) self.actual: a string representation of the misinterpreted phrase
        (b) self.expected: a string representation of the correct interpretation of the phrase
    """
    def __init__(self, actual, expected):
        self.actual = actual
        self.expected = expected
