# Default sr API is Google Web Speech API
# Only use the default key for testing (50 requests/day)
# DO NOT USE THIS API FOR FINAL PROJECT

import speech_recognition as sr
import json

KEYWORDS_PATH = "../res/keywords.txt"

try:
    keywords_file = open(KEYWORDS_PATH)
    keywords = [line.rstrip('\n') for line in keywords_file]
    keywords_file.close()
except:
    print("Keywords file not found.")
    quit(1)

r = sr.Recognizer()
sr.pause_threshold = 0.5
mic = sr.Microphone()

def is_valid(input_words):
    for word in input_words:
        if word not in keywords:
            return False
    return True

def gather_input(s):
    result = []
    temp_alpha = ""
    
    for char in s:
        if char.isdigit():
            result.append(temp_alpha)
            temp_alpha = ""
            result.append(char)
        elif char == ' ':
            result.append(temp_alpha)
            temp_alpha = ""
        else:
            temp_alpha += char
    result.append(temp_alpha)

    # Remove empty parts of result and
    # fix commonly misinterpreted words
    for i, part in enumerate(result):
        if part == '': 
            result.remove(part)
        elif part == "brooke":
            result[i] = "rook"
        elif part == "rookie":
            result[i] = "rook"
            result.insert(i + 1, "e")
        elif part == "for":
            result[i] = "4"
    if result[0] == "9" and result[1].isdigit(): # ninety-four means Knight E4
        result = ["knight", "e", result[1]]

    if (is_valid(result)):
        return result
    else:
        return []

def adjust_for_ambient_noise(sample_duration):
    with mic as source:
        print("Adjusting for ambient noise")
        r.adjust_for_ambient_noise(source, sample_duration)

def get_voice_commands():
    user_input = []
    print("\n********\nListening...\n")
    with mic as source:
        audio = r.listen(source)

    try:
        recognition_guesses = r.recognize_google(audio, show_all=True)['alternative']
        speech_detected = True
        
    except:
        speech_detected = False
        print("No speech detected\n********\n")

    if (speech_detected):
        
        # Get keywords from first (and most likely correct) guess
        first_guess = recognition_guesses[0]['transcript'].lower()
        user_input = gather_input(first_guess)

        # If first guess is not valid input,
        # check if remainding guesses are valid
        if (user_input == []):
            for raw_guess in recognition_guesses:
                formatted_guess = raw_guess['transcript'].lower()
                user_input = gather_input(formatted_guess)
                if (user_input != []):
                    break

        print(user_input)
        print("Google API response: " + str(recognition_guesses))
        print("********\n")
        
    return user_input
