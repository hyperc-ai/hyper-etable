"""Various utility functions"""


import string
import unidecode


def get_char_from_index(idx):
    if idx >= len(string.ascii_lowercase):
        raise ValueError(f"Unsupport index {idx} out of length \"{string.ascii_lowercase}\" ")
    return string.ascii_lowercase[idx].upper()


def get_index_from_char(ch):
    char = ch.lower()
    if len(char) > 1:
        raise ValueError(f"Unsupport index {char} out of \"{string.ascii_lowercase}\" ")
    return string.ascii_lowercase.index(char)


def letter_index_next(letter=''):
    """
        Generate next alphabet index
    """
    if len(letter) == 0:
        return 'A'
    char_index = letter.upper()
    if char_index[-1] != 'Z':
        next_char = string.ascii_uppercase[string.ascii_uppercase.find(char_index[-1])+1]
        return char_index[:-1] + next_char
    else:
        return letter_index_next(letter[:-1]) + 'A'

def str_to_py(sheet_name: str):
    trans_name = unidecode.unidecode(sheet_name).replace(' ', '_').upper()
    trans_name = list(trans_name)
    for i, character in enumerate(trans_name):
        if character not in (string.ascii_uppercase + string.digits + "_"):
            trans_name[i] = "_"
    return f"{''.join(trans_name)}".strip('_')

def sheet_to_py(sheet_name: str):
    return f"tbl_{str_to_py(sheet_name)}"