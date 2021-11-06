def increment_value(selected_data_row : DATA_Class):
    assert selected_data_row.CURRENT_VALUE < DATA.VARIABLES_2.TARGET_VALUE
    selected_data_row.CURRENT_VALUE += 1

def check_target_achieved(selected_data_row : DATA_Class):
    assert selected_data_row.CURRENT_VALUE == DATA.VARIABLES_2.TARGET_VALUE
    DATA.GOAL                              =  True