import hyperc.util


class PlainCell:
    def __init__(self, filename, sheet, letter, number):
        self.filename = filename
        self.sheet = sheet
        self.letter = letter
        self.number = int(number)

    def __hash__(self):
        return hash(self.filename) & hash(self.sheet) & hash(self.letter) & hash(self.number)

    def __str__(self):
        return f'[{self.filename}]{self.sheet}!{self.letter}{self.number}'

    def __eq__(self, other):
        return hash(self) == hash(other)

class PlainCellRange:
    def __init__(self, filename, sheet, letter, number):
        self.filename = filename
        self.sheet = sheet
        assert isinstance(letter,list)
        self.letter = letter # is list
        assert isinstance(number, list)
        self.number = [int(n) for n in number]

    def __hash__(self):
        return hash(self.filename) & hash(self.sheet) & hash(self.letter) & hash(self.number)

    def __str__(self):
        return f'[{self.filename}]{self.sheet}!{self.letter[0]}{self.number[0]}:{self.letter[1]}{self.number[1]}'

    def __eq__(self, other):
        return hash(self) == hash(other)

class PlainCellNamedRange:
    def __init__(self, filename, sheet, name):
        self.filename = filename
        self.sheet = sheet
        self.name = name

    def __hash__(self):
        return hash(self.filename) & hash(self.sheet) & hash(self.name)

    def __str__(self):
        return f'[{self.filename}]{self.sheet}!{self.name}'

    def __eq__(self, other):
        return hash(self) == hash(other)
