from xlsx_to_py.classes import *

def aa(gg:SHEET1_Class):
    assert gg.HEADER2 == 'bad'
    gg.HEADER1 = 1
    gg.HEADER2 = 'good100500'

def real_good(gg:SHEET1_Class):
    assert gg.HEADER2 == 'good100500'
    gg.HEADER1 = 2
    gg.HEADER2 = 'ooh' 
    gg.HEADER2 = 'bad'
    DATA.GOAL=True    
