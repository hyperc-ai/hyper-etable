class MyClass:
    a:int
    def __init__(self):
        self.a=1

b=MyClass()

def aa(gg:SHEET1_Class):
    my_class = MyClass()
    assert gg.HEADER2 == 'bad'
    gg.HEADER1 = 1
    gg.HEADER2 = 'good100500'

def real_good(gg:SHEET1_Class, mm:MyClass):
    assert gg.HEADER2 == 'good100500'
    gg.HEADER_USER=1
    mm.a += 1
    gg.HEADER1 = 2
    gg.HEADER2 = 'ooh'
    gg.HEADER_USER += 2
    gg.HEADER_USER_SET.add(1)

def real_good2(gg:SHEET1_Class, mm:MyClass):
    assert mm.a == 2
    assert gg.HEADER_USER == 3
    assert 1 in gg.HEADER_USER_SET
    DATA.GOAL=True
