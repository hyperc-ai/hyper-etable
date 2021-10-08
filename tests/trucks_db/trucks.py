def move_forward(t:TRANSPORT_Class, l_a:LOCATION_ADJACENCY_Class):
    assert t.LOCATION == l_a.LOCATION_A
    t.LOCATION = l_a.LOCATION_B

def my_truck_finish(t:TRANSPORT_Class):
    assert t.LOCATION == 'LocC'
    assert t.NAME == 'MyTruck1'
    DATA.GOAL=True    
