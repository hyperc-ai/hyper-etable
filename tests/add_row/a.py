def aa(gg:SHEET1_Class):
    assert gg.HEADER2 == 'bad'
    gg.HEADER1 = 1
    gg.HEADER2 = 'good100500'

def real_good(gg:SHEET1_Class):
    assert gg.HEADER2 == 'good100500'
    gg.HEADER1 = 2
    gg.HEADER2 = 'ooh'
    
    new_row=SHEET1_Class()
    # new_row.HEADER1 = 7
    # new_row.HEADER2 = 'new row'

    # HCT_OBJECTS['SHEET1'].append(new_row)

    DATA.GOAL=True    
