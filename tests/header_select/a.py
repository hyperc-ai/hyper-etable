def aa(gg:SHEET1_Class):
    assert gg.HEADER2 == 'bad'
    gg.HEADER1 = 1
    gg.HEADER2 = 'good'
    HCT_STATIC_OBJECT.GOAL=True    
