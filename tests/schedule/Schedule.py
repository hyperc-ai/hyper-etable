def plan_resource_monday(selected_demand : INPUT_DEMAND_Class, selected_resource : INPUT_RESOURCE_Class):
    assert selected_demand.MONDAY == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    selected_demand.MONDAY = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

def plan_resource_tuesday(selected_demand : INPUT_DEMAND_Class, selected_resource : INPUT_RESOURCE_Class):
    assert selected_demand.TUESDAY == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    selected_demand.TUESDAY = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

def plan_resource_wednesday(selected_demand : INPUT_DEMAND_Class, selected_resource : INPUT_RESOURCE_Class):
    assert selected_demand.WEDNESDAY == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    selected_demand.WEDNESDAY = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

def plan_resource_thursday(selected_demand : INPUT_DEMAND_Class, selected_resource : INPUT_RESOURCE_Class):
    assert selected_demand.THURSDAY == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    selected_demand.THURSDAY = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

def plan_resource_friday(selected_demand : INPUT_DEMAND_Class, selected_resource : INPUT_RESOURCE_Class):
    assert selected_demand.FRIDAY == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    selected_demand.FRIDAY = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

def plan_resource_saturday(selected_demand : INPUT_DEMAND_Class, selected_resource : INPUT_RESOURCE_Class):
    assert selected_demand.SATURDAY == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    selected_demand.SATURDAY = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

def plan_resource_sunday(selected_demand : INPUT_DEMAND_Class, selected_resource : INPUT_RESOURCE_Class):
    assert selected_demand.SUNDAY == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    selected_demand.SUNDAY = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

def all_shifts_planned():
    assert DATA.VARIABLES_2.PLANNED_SHIFTS == DATA.VARIABLES_2.COUNT_SHIFTS
    DATA.GOAL = True




