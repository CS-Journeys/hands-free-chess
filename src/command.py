class Command:
    def __init__(self, data):
        self.data = data
        self.length = len(self.data)

    def text(self):
        return ' '.join(self.data)


class MoveCommand:
    def __init__(self, data):
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

    def text(self):
        return self.piece_name.capitalize() + " to " + self.dest_col.upper() + self.dest_row

    def get_src(self):
        if self.src_col is None or self.src_row is None:
            return None
        else:
            return self.src_col, self.src_row

    def get_dest(self):
        return self.dest_col, self.dest_row
