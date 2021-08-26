class MyClass:
    def __init__(self):
        self.a=1

def aa(gg:SHEET1_Class):
    my_class = MyClass()
    assert gg.HEADER2 == 'bad'
    gg.HEADER1 = 1
    gg.HEADER2 = 'good100500'

def real_good(gg:SHEET1_Class, mm:MyClass):
    assert gg.HEADER2 == 'good100500'
    assert mm.a == 1
    gg.HEADER1 = 2
    gg.HEADER2 = 'ooh' 
    DATA.GOAL=True
