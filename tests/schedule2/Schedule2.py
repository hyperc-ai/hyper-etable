def plan_resource(selected_demand : DEMAND_LIST_Class, selected_resource : INPUT_RESOURCE_Class, selected_resource_cost: RESOURCE_COSTS_Class):
    assert selected_demand.DEMAND == "V"
    assert selected_demand.ROOM == selected_resource.ROOM
    assert DATA.VARIABLES_2.PLANNED_SHIFTS < DATA.VARIABLES_2.COUNT_SHIFTS
    assert selected_resource_cost.RESOURCE == selected_resource.RESOURCE
    assert selected_resource_cost.COST == DATA.VARIABLES_2.CURRENT_COST_LEVEL
    DATA.VARIABLES_2.CURRENT_COST_LEVEL = 1
    selected_demand.DEMAND = selected_resource.RESOURCE
    DATA.VARIABLES_2.PLANNED_SHIFTS += 1

 

def increase_cost_level():
    assert DATA.VARIABLES_2.CURRENT_COST_LEVEL < DATA.VARIABLES_2.MAXIMUM_COST_LEVEL
    DATA.VARIABLES_2.CURRENT_COST_LEVEL += 1

def all_shifts_planned():
    assert DATA.VARIABLES_2.PLANNED_SHIFTS == DATA.VARIABLES_2.COUNT_SHIFTS
    DATA.GOAL = True




