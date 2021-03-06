import hyper_etable.run_util
import hyper_etable.etable
import pathlib
import inspect

def test_add_row():
    xlsx_file=pathlib.Path('./tests/add_row/has_header_sort_bad.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    hyper_etable.run_util.simple_run(
        input_xlsx_filename=xlsx_file,
        input_py_filename='./tests/add_row/a.py',
        # output_plan_filename='./tests/add_row/a_plan.py',
        output_xlsx_filename='./tests/add_row/result_has_header.xlsx',
        output_classes_filename='./tests/add_row/classes_aaa.py',
        has_header=True) 

def test_add_row_model_test():
    xlsx_file=pathlib.Path('./tests/add_row/has_header_sort_bad.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    project_name=inspect.currentframe().f_code.co_name
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.open_dump(has_header=True, addition_python_files=['./tests/add_row/a.py'])
    et.mod.aa(gg=et.mod.DATA.SHEET1_4)
    et.mod.real_good(gg=et.mod.DATA.SHEET1_4)
    et.mod.hct_main_goal()
    et.save_dump(out_filename='./tests/add_row/result_has_header_model_test123.xlsx')


def test_hypercrm1():
    xlsx_file = pathlib.Path('./tests/hypercrm1/HyperCRM.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    project_name=inspect.currentframe().f_code.co_name
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.open_dump(has_header=True, addition_python_files=['./tests/hypercrm1/HyperCRM.py'])
    et.mod.a2_send_invitation_through_linkedIn_contact(
        lead=et.mod.DATA.LEAD_2, task=et.mod.DATA.TASK_2, contact=et.mod.DATA.CONTACT_158)
    et.mod.hct_main_goal()
    et.save_dump(out_filename='./tests/hypercrm1/result_HyperCRM_many_to_many.xlsx')
    # print(f"\ntest file {xlsx_file}", end='')
    # hyper_etable.run_util.simple_run(
    #     input_xlsx_filename=xlsx_file,
    #     input_py_filename='./tests/hypercrm1/HyperCRM_many_to_many.py',
    #     # output_plan_filename='./tests/add_row/a_plan.py',
    #     output_xlsx_filename='./tests/hypercrm1/out/result.xlsx',
    #     output_classes_filename='./tests/hypercrm1/out/classes_aaa.py',
        # has_header=True) 
