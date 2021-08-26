import hyper_etable.run_util
import hyper_etable.etable
import pathlib

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

