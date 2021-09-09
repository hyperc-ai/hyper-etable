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

# def test_add_row_report():
#     xlsx_file=pathlib.Path('./tests/add_row/has_header_sort_bad.xlsx')
#     print(f"\ntest file {xlsx_file}", end='')
#     hyper_etable.run_util.simple_run(
#         input_xlsx_filename=xlsx_file,
#         input_py_filename='./tests/add_row/a_report.py',
#         output_xlsx_filename='./tests/add_row/result_has_header_report.xlsx',
#         output_classes_filename='./tests/add_row/classes_a_report.py',
#         has_header=True) 

def test_add_row_model_test():
    xlsx_file=pathlib.Path('./tests/add_row/has_header_sort_bad.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    project_name=inspect.currentframe().f_code.co_name
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.open_dump(has_header=True, addition_python_files=['./tests/add_row/a_add.py'])
    et.mod.aa(gg=et.mod.DATA.SHEET1_4)
    et.mod.real_good(gg=et.mod.DATA.SHEET1_4)
    et.mod.hct_main_goal()
    et.save_dump(out_filename='./tests/add_row/result_has_header_model_test.xlsx')

def test_add_row_add():
    xlsx_file=pathlib.Path('./tests/add_row/has_header_sort_bad.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    hyper_etable.run_util.simple_run(
        input_xlsx_filename=xlsx_file,
        input_py_filename='./tests/add_row/a_add.py',
        # output_plan_filename='./tests/add_row/a_plan.py',
        output_xlsx_filename='./tests/add_row/result_has_header.xlsx',
        output_classes_filename='./tests/add_row/classes_aaa.py',
        has_header=True) 

