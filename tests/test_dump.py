import hyper_etable.run_util
import hyper_etable.etable
import pathlib


def test_dump():
    xlsx_file=pathlib.Path('./tests/dump/dump_me.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    hyper_etable.run_util.run(
        input_xlsx_filename=xlsx_file,
        input_py_filename='./tests/dump/gg.py',
        output_plan_filename='./tests/dump/plan.py',
        output_xlsx_filename='./tests/dump/result.xlsx',
        output_classes_filename='./tests/dump/classes_dump.py',
        has_header=False)

def test_header():
    xlsx_file=pathlib.Path('./tests/header_select/has_header.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    hyper_etable.run_util.run(
        input_xlsx_filename=xlsx_file,
        input_py_filename='./tests/header_select/a.py',
        output_plan_filename='./tests/header_select/a_plan.py',
        output_xlsx_filename='./tests/header_select/result_has_header.xlsx',
        output_classes_filename='./tests/dump/classes_aaa.py',
        has_header=True) 
