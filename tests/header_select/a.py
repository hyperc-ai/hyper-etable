
new_line=SHEET1_Class()
new_line.HEADER_USER_SET=set()

def aa(gg:SHEET1_Class):
    assert gg.HEADER2 == 'bad'
    gg.HEADER1 = 1
    gg.HEADER2 = 'good100500'

def real_good(gg:SHEET1_Class):
    assert gg.HEADER2 == 'good100500'
    gg.HEADER1 = 2
    gg.HEADER2 = 'ooh' 
    DATA.GOAL=True    
