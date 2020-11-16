# Default sr API is Google Web Speech API
# Only use the default key for testing (50 requests/day)
# DO NOT USE THIS API FOR FINAL PROJECT

# Documentation note: functions which start with underscore are "private"

import speech_recognition as sr
import json

KEYWORDS_PATH = "res/keywords.txt"

# Open keywords file
try:
    keywords_file = open(KEYWORDS_PATH)
    keywords = [line.rstrip('\n') for line in keywords_file]
    keywords_file.close()
except:
    print("Keywords file not found.")
    quit(1)

# Initialize voice recognition objects
r = sr.Recognizer()
sr.pause_threshold = 0.5
mic = sr.Microphone()


#############################################################################
# Description : Check if an array of strings only contains keywords
# Parameters  : input_words is an array of lowercase strings
# Return      : False if any string in array is not listed in keywords file
#               True if all strings in the array are listed in keywords file
def _is_comprised_of_keywords(words_array):
    for word in words_array:
        if word not in keywords:
            return False
    return True


#############################################################################
# Description : split string into an array of strings
# Parameters  : a lowercase string, potentially made up of multiple words and numbers
# Return      : an array of strings
# Example     : _split_string_into_array("knight g4") returns ["knight", "g", "4"]
def _split_string_into_array(my_string):
    my_array = []
    temp_alpha = ""

    # Split string into parts
    for char in my_string:
        if char.isdigit():
            my_array.append(temp_alpha)
            temp_alpha = ""
            my_array.append(char)
        elif char == ' ':
            my_array.append(temp_alpha)
            temp_alpha = ""
        else:
            temp_alpha += char
    my_array.append(temp_alpha)

    # Remove empty parts of array
    for i, part in enumerate(my_array):
        if part == '': 
            my_array.remove(part)

    return my_array


#############################################################################
# Description : Fix commonly misinterpreted words
# Parameters  : an array of lowercase strings
# Return      : the same array but with corrected words
# Example     : _fix_common_misinterpretations(["rookie", "4"]) returns ["rook", "e", "4"]
def _fix_common_misinterpretations(my_array):
    for i, part in enumerate(my_array):
        if part == "brooke":
            my_array[i] = "rook"
        elif part == "rookie":
            my_array[i] = "rook"
            my_array.insert(i + 1, "e")
        elif part == "for":
            my_array[i] = "4"
        elif part == "at":
            my_array[i] = "f"
    if my_array[0] == "9" and my_array[1].isdigit(): # ninety-four means Knight E4
        my_array = ["knight", "e", my_array[1]]

    return my_array


#############################################################################
# Description : Adjust microphone so that it ignores ambient noise
# Parameters  : a number in seconds
# Return      : none
def adjust_for_ambient_noise(sample_duration):
    with mic as source:
        print("Adjusting for ambient noise")
        r.adjust_for_ambient_noise(source, sample_duration)


#############################################################################
# Description : Get voice command from microphone/API and process the results
# Return      : an array of strings
# Example     : If the user says "Knight G4", the function returns ["knight", "g", "4"]
# TO-DO       : If the user says "Knight to G4", the function should still return ["knight", "g", "4"]
def get_voice_commands():
    user_input = [] # user_input will contain the keywords that the user spoke

    # Listen to audio with microphone
    print("\n********\nListening...\n")
    with mic as source:
        audio = r.listen(source)

    # Try to interpet audio with Google Speech API
    try:
        recognition_guesses = r.recognize_google(audio, show_all=True)['alternative']
        speech_detected = True
        
    except:
        speech_detected = False
        print("No speech detected\n********\n")

    # Process Google Speech API results if the API returned something to process
    if (speech_detected):
        
        # Get keywords from first (and most likely correct) guess
        first_guess = recognition_guesses[0]['transcript'].lower()
        user_input = _split_string_into_array(first_guess)
        user_input = _fix_common_misinterpretations(user_input)
        
        # If first guess is not uniquely made up of keywords,
        # check if remainding guesses are valid
        if (not _is_comprised_of_keywords(user_input)):
            for raw_guess in recognition_guesses:
                lowercase_guess = raw_guess['transcript'].lower()
                user_input = _split_string_into_array(lowercase_guess)
                user_input = _fix_common_misinterpretations(user_input)
                if (_is_comprised_of_keywords(user_input)):
                    break

        # If, after having checked all guesses by the API, user_input is still not uniquely comprised of keywords,
        # then set user_input to an empty array.
        # The empty array means that the user did not exclusively say words that were understood by our dictionary
        if (not _is_comprised_of_keywords(user_input)):
            user_input = []

        print("Google API response: " + str(recognition_guesses))
        print("User input: " + str(user_input) + "\n")
        print("********\n")
        
    return user_input
