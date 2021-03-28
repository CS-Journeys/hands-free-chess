"""
This file defines Command and MoveCommand, two important classes for handling the user's commands.

Note that in pure Object-Oriented Programming, the two classes would be implemented using inheritance.
In Python, inheritance isn't necessary.
"""

class Command:
    """
    A Command object represents a non-move command such as "Cancel," "Exit," "Change color," etc.
    A Command object has:
        (a) data: a list of lowercase strings that represents the command (ex: ["change", "color"])
        (b) length: the number of words that make up the command
        (c) text(): a function to convert the command into a single string representation
            (ex: ["change", "color"] --> "change color")
    """

    ''' CONSTRUCTOR '''
    def __init__(self, data):
        self.data = data
        self.length = len(self.data)

    ''' PUBLIC '''
    def text(self):
        """
        This function returns a single string representation of the Command object.
        """
        return ' '.join(self.data)


class MoveCommand:
    """
    A MoveCommand object represents a move command such as "Knight G4," "Pawn E3 to E5," etc.
    A MoveCommand object has:
        (a) data: a list of lowercase strings that represents the command
        (b) length: the number of words that make up the command
        (c) text(): a function to convert the command into a single string representation
            (ex: ["knight", "g", "4"] --> "Knight to G4")
        (d) getters for the move's source and destination locations
    """

    ''' CONSTRUCTOR '''
    def __init__(self, data):
        """
        Parameters:
            - data: a list of lowercase strings that represent a move and may or may not include the string "to".
        """

        self.data = data
        self.length = len(self.data)
        if 'to' in self.data:
            self.data.remove('to')
        self.piece_name = self.data[0]
        if len(self.data) == 3:
            self.src_col = None
            self.src_row = None
            self.dest_col = self.data[1]
            self.dest_row = self.data[2]
        elif len(self.data) == 5:
            self.src_col = self.data[1]
            self.src_row = self.data[2]
            self.dest_col = self.data[3]
            self.dest_row = self.data[4]
        else:
            # TODO: logging and error msg stuff
            raise ValueError

    ''' PUBLIC '''
    def text(self):
        """
        This function returns a single string representation of the MoveCommand object.
        """
        return self.piece_name.capitalize() + " to " + self.dest_col.upper() + self.dest_row

    def get_src(self):
        """
        This function returns a copy of the move's source location.
        If the source location is undefined, return None.

        Example:
            "Knight E4 to G5" --> get_src() returns ("e", "4")
        """
        if self.src_col is None or self.src_row is None:
            return None
        else:
            return self.src_col, self.src_row

    def get_dest(self):
        """
        This function returns a copy of the move's destination location.

        Example:
            "Knight E4 to G5" --> get_dest() returns ("g", "5")
        """
        return self.dest_col, self.dest_row
