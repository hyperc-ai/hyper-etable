from typing import Set

class TableElementMeta(type): #hyper-etable auto generated line
    pass #hyper-etable auto generated line
    def __init__(self): #hyper-etable auto generated line
        pass #hyper-etable auto generated line

class SHEET1_Class: #hyper-etable auto generated line
    __table_name__: str #hyper-etable auto generated line
    addidx: int #hyper-etable auto generated line
    HEADER_USER: int
    HEADER_USER_SET: Set[int]
    def __init__(self): 
        self.__table_name__ = "SHEET1" #hyper-etable auto generated line
        self.__xl_sheet_name__ = "Sheet1" #hyper-etable auto generated line
        self.HEADER_USER = 0
        self.HEADER_USER_SET = set()

class StaticObject: #hyper-etable auto generated line
    SHEET1_1: SHEET1_Class #hyper-etable auto generated line
    SHEET1_2: SHEET1_Class #hyper-etable auto generated line
    SHEET1_3: SHEET1_Class #hyper-etable auto generated line
    SHEET1_4: SHEET1_Class #hyper-etable auto generated line
    SHEET1_5: SHEET1_Class #hyper-etable auto generated line
    SHEET1_6: SHEET1_Class #hyper-etable auto generated line
    SHEET1_7: SHEET1_Class #hyper-etable auto generated line
    SHEET1_8: SHEET1_Class #hyper-etable auto generated line
    SHEET1_9: SHEET1_Class #hyper-etable auto generated line
    SHEET1_10: SHEET1_Class #hyper-etable auto generated line
    SHEET1_11: SHEET1_Class #hyper-etable auto generated line
    SHEET1_addidx: int #hyper-etable auto generated line
    GOAL: bool #hyper-etable auto generated line
    def __init__(self): #hyper-etable auto generated line
        pass #hyper-etable auto generated line

class DefinedTables: #hyper-etable auto generated line
    pass #hyper-etable auto generated line
    def __init__(self):
        pass #hyper-etable auto generated line

DATA = StaticObject()


gg=SHEET1_Class()