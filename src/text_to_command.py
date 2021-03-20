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

class CommandFormat:
    def __init__(self, name, components):
        self.name = name
        self.components = components
        self.length = len(components)

    def get_word_type(self, ndx):
        if ndx < self.length:
            return self.components[ndx]
        else:
            return ""

class Misinterpretation:
    def __init__(self, actual, expected):
        self.actual = actual
        self.expected = expected


class TextToCmdBuffer:
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

    def add_text(self, raw_text):
        self.log.debug(f"Before text addition: {self.words}")

        # Make the text lowercase
        lower_text = raw_text.lower()

        # Split up the single string into multiple words
        new_words = self._split_into_words(lower_text)

        # Fix misinterpretations that the Speech Recognizer commonly makes
        self._fix_misinterpretations(new_words)

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
        If not, return None.

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
        self.words = []

    def _fix_misinterpretations(self, words):
        """
        Fix commonly misinterpreted words.

        Parameters:
            - words: a list of strings
        Return:
            - words: the fixed words
        """
        for i, word in enumerate(words):
            for misinterpretation in self.misinterpretations:
                if word == misinterpretation.actual:
                    # Replace the actual word with the expected words
                    words.pop(i)
                    words[i:i] = self._split_into_words(misinterpretation.expected)

        return words

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
