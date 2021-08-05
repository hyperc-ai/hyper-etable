class TableElementMeta(type):
    pass
    def __init__(self):
        pass

class INPUT_RESOURCE_Class:
    __table_name__: str
    RESOURCE: str
    ROOM: str
    def __init__(self):
        self.__table_name__ = "INPUT_RESOURCE"
        self.__xl_sheet_name__ = "Input_Resource"

class RESOURCE_COSTS_Class:
    __table_name__: str
    RESOURCE: str
    COST: str
    def __init__(self):
        self.__table_name__ = "RESOURCE_COSTS"
        self.__xl_sheet_name__ = "Resource_costs"

class INPUT_DEMAND_Class:
    __table_name__: str
    ROOM: str
    MONDAY: str
    TUESDAY: str
    WEDNESDAY: str
    FRIDAY: str
    SATURDAY: str
    SUNDAY: str
    SHIFTS_TOTAL: str
    THURSDAY: str
    def __init__(self):
        self.__table_name__ = "INPUT_DEMAND"
        self.__xl_sheet_name__ = "Input_Demand"

class VARIABLES_Class:
    __table_name__: str
    PLANNED_SHIFTS: str
    COUNT_SHIFTS: str
    CURRENT_COST_LEVEL: str
    MAXIMUM_COST_LEVEL: str
    def __init__(self):
        self.__table_name__ = "VARIABLES"
        self.__xl_sheet_name__ = "Variables"

class COST_REPORT_Class:
    __table_name__: str
    def __init__(self):
        self.__table_name__ = "COST_REPORT"
        self.__xl_sheet_name__ = "Cost_report"

class StaticObject:
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
    RESOURCE_COSTS_1: RESOURCE_COSTS_Class
    RESOURCE_COSTS_2: RESOURCE_COSTS_Class
    RESOURCE_COSTS_3: RESOURCE_COSTS_Class
    RESOURCE_COSTS_4: RESOURCE_COSTS_Class
    RESOURCE_COSTS_5: RESOURCE_COSTS_Class
    RESOURCE_COSTS_6: RESOURCE_COSTS_Class
    RESOURCE_COSTS_7: RESOURCE_COSTS_Class
    RESOURCE_COSTS_8: RESOURCE_COSTS_Class
    INPUT_DEMAND_1: INPUT_DEMAND_Class
    INPUT_DEMAND_2: INPUT_DEMAND_Class
    INPUT_DEMAND_3: INPUT_DEMAND_Class
    INPUT_DEMAND_4: INPUT_DEMAND_Class
    INPUT_DEMAND_5: INPUT_DEMAND_Class
    INPUT_DEMAND_6: INPUT_DEMAND_Class
    VARIABLES_1: VARIABLES_Class
    VARIABLES_2: VARIABLES_Class
    COST_REPORT_1: COST_REPORT_Class
    COST_REPORT_2: COST_REPORT_Class
    COST_REPORT_3: COST_REPORT_Class
    COST_REPORT_4: COST_REPORT_Class
    COST_REPORT_5: COST_REPORT_Class
    COST_REPORT_6: COST_REPORT_Class
    COST_REPORT_7: COST_REPORT_Class
    COST_REPORT_8: COST_REPORT_Class
    COST_REPORT_9: COST_REPORT_Class
    COST_REPORT_10: COST_REPORT_Class
    COST_REPORT_11: COST_REPORT_Class
    COST_REPORT_12: COST_REPORT_Class
    COST_REPORT_13: COST_REPORT_Class
    COST_REPORT_14: COST_REPORT_Class
    COST_REPORT_15: COST_REPORT_Class
    COST_REPORT_16: COST_REPORT_Class
    COST_REPORT_17: COST_REPORT_Class
    COST_REPORT_18: COST_REPORT_Class
    GOAL: bool
    def __init__(self):
        pass

class DefinedTables:
    GOAL: bool
    def __init__(self):
        pass

DATA = StaticObject()
