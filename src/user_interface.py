# TODO: amazing UI initialization stuff
# TODO: add start/stop buttons

import PySimpleGUI as sg
from main import main
import time

check = True
msg = ["1", "2", "3"]
messages = list(msg);
headings = ['Message']
sg.theme("DarkAmber")
layout = [[sg.Table(values=messages[:][:],
                    headings=headings,
                    col_widths=[300],
                    max_col_width=25,
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification='right',
                    num_rows=max(len(messages), 15),
                    alternating_row_color='yellow',
                    key='-TABLE-',
                    row_height=35)],
          [sg.Button("Start")], [sg.Button("Stop")]]

window = sg.Window("Hands Free Chess", layout)
table = window.FindElement('-TABLE-')

def print_to_user(message):
    messages.append(message)
    window.write_event_value("Table", messages)

# Create an event loop
while check:
    event, value = window.read()

    if event == "Start":
        main.main()
        # print_to_user("Hello")
        # print_to_user("World")
    elif event == "Table":
        window['-TABLE-'].update(values=messages[:][:])
    elif event == "Stop" or event == sg.WIN_CLOSED:
        check = False
        window.close()
        exit(0)
    print("true")

    # End program if user closes window or
    # presses the OK button
