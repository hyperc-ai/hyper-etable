class TableElementMeta(type):
    pass
    def __init__(self):
        pass

class RESOURCE_COSTS_Class:
    __table_name__: str
    RESOURCE: str
    COST: str
    def __init__(self):
        self.__table_name__ = "RESOURCE_COSTS"
        self.__xl_sheet_name__ = "Resource_costs"

class INPUT_RESOURCE_Class:
    __table_name__: str
    RESOURCE: str
    ROOM: str
    def __init__(self):
        self.__table_name__ = "INPUT_RESOURCE"
        self.__xl_sheet_name__ = "Input_Resource"

class INPUT_DEMAND_Class:
    __table_name__: str
    ROOM: str
    MONDAY: str
    TUESDAY: str
    WEDNESDAY: str
    THURSDAY: str
    FRIDAY: str
    SATURDAY: str
    SUNDAY: str
    SHIFTS_TOTAL: str
    def __init__(self):
        self.__table_name__ = "INPUT_DEMAND"
        self.__xl_sheet_name__ = "Input_Demand"

class DEMAND_LIST_Class:
    __table_name__: str
    ROOM_ID: str
    DAY: str
    ROOM: str
    DEMAND: str
    def __init__(self):
        self.__table_name__ = "DEMAND_LIST"
        self.__xl_sheet_name__ = "Demand_list"

class VARIABLES_Class:
    __table_name__: str
    PLANNED_SHIFTS: str
    COUNT_SHIFTS: str
    CURRENT_COST_LEVEL: str
    MAXIMUM_COST_LEVEL: str
    def __init__(self):
        self.__table_name__ = "VARIABLES"
        self.__xl_sheet_name__ = "Variables"

class StaticObject:
    RESOURCE_COSTS_1: RESOURCE_COSTS_Class
    RESOURCE_COSTS_2: RESOURCE_COSTS_Class
    RESOURCE_COSTS_3: RESOURCE_COSTS_Class
    RESOURCE_COSTS_4: RESOURCE_COSTS_Class
    RESOURCE_COSTS_5: RESOURCE_COSTS_Class
    RESOURCE_COSTS_6: RESOURCE_COSTS_Class
    RESOURCE_COSTS_7: RESOURCE_COSTS_Class
    RESOURCE_COSTS_8: RESOURCE_COSTS_Class
    INPUT_RESOURCE_1: INPUT_RESOURCE_Class
    INPUT_RESOURCE_2: INPUT_RESOURCE_Class
    INPUT_RESOURCE_3: INPUT_RESOURCE_Class
    INPUT_RESOURCE_4: INPUT_RESOURCE_Class
    INPUT_RESOURCE_5: INPUT_RESOURCE_Class
    INPUT_RESOURCE_6: INPUT_RESOURCE_Class
    INPUT_RESOURCE_7: INPUT_RESOURCE_Class
    INPUT_RESOURCE_8: INPUT_RESOURCE_Class
    INPUT_RESOURCE_9: INPUT_RESOURCE_Class
    INPUT_RESOURCE_10: INPUT_RESOURCE_Class
    INPUT_RESOURCE_11: INPUT_RESOURCE_Class
    INPUT_DEMAND_1: INPUT_DEMAND_Class
    INPUT_DEMAND_2: INPUT_DEMAND_Class
    INPUT_DEMAND_3: INPUT_DEMAND_Class
    INPUT_DEMAND_4: INPUT_DEMAND_Class
    INPUT_DEMAND_5: INPUT_DEMAND_Class
    INPUT_DEMAND_6: INPUT_DEMAND_Class
    INPUT_DEMAND_7: INPUT_DEMAND_Class
    DEMAND_LIST_1: DEMAND_LIST_Class
    DEMAND_LIST_2: DEMAND_LIST_Class
    DEMAND_LIST_3: DEMAND_LIST_Class
    DEMAND_LIST_4: DEMAND_LIST_Class
    DEMAND_LIST_5: DEMAND_LIST_Class
    DEMAND_LIST_6: DEMAND_LIST_Class
    DEMAND_LIST_7: DEMAND_LIST_Class
    DEMAND_LIST_8: DEMAND_LIST_Class
    DEMAND_LIST_9: DEMAND_LIST_Class
    DEMAND_LIST_10: DEMAND_LIST_Class
    DEMAND_LIST_11: DEMAND_LIST_Class
    DEMAND_LIST_12: DEMAND_LIST_Class
    DEMAND_LIST_13: DEMAND_LIST_Class
    DEMAND_LIST_14: DEMAND_LIST_Class
    DEMAND_LIST_15: DEMAND_LIST_Class
    DEMAND_LIST_16: DEMAND_LIST_Class
    DEMAND_LIST_17: DEMAND_LIST_Class
    DEMAND_LIST_18: DEMAND_LIST_Class
    DEMAND_LIST_19: DEMAND_LIST_Class
    DEMAND_LIST_20: DEMAND_LIST_Class
    DEMAND_LIST_21: DEMAND_LIST_Class
    DEMAND_LIST_22: DEMAND_LIST_Class
    DEMAND_LIST_23: DEMAND_LIST_Class
    DEMAND_LIST_24: DEMAND_LIST_Class
    DEMAND_LIST_25: DEMAND_LIST_Class
    DEMAND_LIST_26: DEMAND_LIST_Class
    DEMAND_LIST_27: DEMAND_LIST_Class
    DEMAND_LIST_28: DEMAND_LIST_Class
    DEMAND_LIST_29: DEMAND_LIST_Class
    DEMAND_LIST_30: DEMAND_LIST_Class
    DEMAND_LIST_31: DEMAND_LIST_Class
    DEMAND_LIST_32: DEMAND_LIST_Class
    DEMAND_LIST_33: DEMAND_LIST_Class
    DEMAND_LIST_34: DEMAND_LIST_Class
    DEMAND_LIST_35: DEMAND_LIST_Class
    DEMAND_LIST_36: DEMAND_LIST_Class
    DEMAND_LIST_37: DEMAND_LIST_Class
    DEMAND_LIST_38: DEMAND_LIST_Class
    DEMAND_LIST_39: DEMAND_LIST_Class
    DEMAND_LIST_40: DEMAND_LIST_Class
    DEMAND_LIST_41: DEMAND_LIST_Class
    DEMAND_LIST_42: DEMAND_LIST_Class
    VARIABLES_1: VARIABLES_Class
    VARIABLES_2: VARIABLES_Class
    GOAL: bool
    def __init__(self):
        pass

class DefinedTables:
    GOAL: bool
    def __init__(self):
        pass

DATA = StaticObject()
