class TableElementMeta(type): 
    pass #hyper-etable auto generated line
    def __init__(self): 
        pass #hyper-etable auto generated line

class TRANSPORT_Class: 
    __table_name__: str #hyper-etable auto generated line
    addidx: int #hyper-etable auto generated line
    NAME: str #hyper-etable auto generated line
    WEIGTH: str #hyper-etable auto generated line
    LOCATION: str #hyper-etable auto generated line
    def __init__(self): 
        self.__table_name__ = "TRANSPORT" #hyper-etable auto generated line
        self.__xl_sheet_name__ = "Transport" #hyper-etable auto generated line

class LOCATION_ADJACENCY_Class: 
    __table_name__: str #hyper-etable auto generated line
    addidx: int #hyper-etable auto generated line
    LOCATION_A: str #hyper-etable auto generated line
    LOCATION_B: str #hyper-etable auto generated line
    def __init__(self): 
        self.__table_name__ = "LOCATION_ADJACENCY" #hyper-etable auto generated line
        self.__xl_sheet_name__ = "Location Adjacency" #hyper-etable auto generated line

class StaticObject: 
    TRANSPORT_1: TRANSPORT_Class #hyper-etable auto generated line
    TRANSPORT_2: TRANSPORT_Class #hyper-etable auto generated line
    LOCATION_ADJACENCY_1: LOCATION_ADJACENCY_Class #hyper-etable auto generated line
    LOCATION_ADJACENCY_2: LOCATION_ADJACENCY_Class #hyper-etable auto generated line
    TRANSPORT_addidx: int #hyper-etable auto generated line
    LOCATION_ADJACENCY_addidx: int #hyper-etable auto generated line
    GOAL: bool #hyper-etable auto generated line
    def __init__(self): 
        pass #hyper-etable auto generated line

class DefinedTables: 
    pass #hyper-etable auto generated line
    def __init__(self): 
        pass #hyper-etable auto generated line

DATA = StaticObject()
