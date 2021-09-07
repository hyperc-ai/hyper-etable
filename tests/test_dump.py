"""PYTEST_DONT_REWRITE"""
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
    xlsx_file=pathlib.Path('./tests/header_select/has_header_sort_bad.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    hyper_etable.run_util.run(
        input_xlsx_filename=xlsx_file,
        input_py_filename='./tests/header_select/a.py',
        output_plan_filename='./tests/header_select/a_plan.py',
        output_xlsx_filename='./tests/header_select/result_has_header.xlsx',
        output_classes_filename='./tests/header_select/classes_a.py',
        has_header=True) 

def test_custom_class():
    xlsx_file=pathlib.Path('./tests/header_select/has_header_sort_bad.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    hyper_etable.run_util.run(
        input_xlsx_filename=xlsx_file,
        input_py_filename='./tests/header_select/a_custom_class.py',
        output_xlsx_filename='./tests/header_select/result_has_header_a_custom_class.xlsx',
        output_plan_filename='./tests/header_select/a_plan_custom_class.py',
        output_classes_filename='./tests/header_select/classes_a_custom_class.py',
        has_header=True)

def test_custom_class_edited():
    xlsx_file=pathlib.Path('./tests/header_select/has_header_sort_bad.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    input_xlsx_filename=xlsx_file
    input_py_filename='./tests/header_select/a_custom_class.py'
    output_xlsx_filename='./tests/header_select/result_has_header_a_custom_class.xlsx'
    output_plan_filename='./tests/header_select/a_plan_custom_class.py'
    input_classes_filename='./tests/header_select/classes_a_custom_class_input.py'
    output_classes_filename='./tests/header_select/classes_a_custom_class.py'
    has_header=True
    et = hyper_etable.etable.ETable(input_xlsx_filename, project_name='test_custom_class_edited')
    et.open_dump(has_header=has_header, addition_python_files=[input_py_filename])
    et.dump_py(out_filename=output_classes_filename) # save classes in py file
    et.solver_call_plan_n_exec() # solve with execution in pddl.py
    et.load_rows_in_table()
    et.save_plan(prefix='DATA.', out_filename=output_plan_filename) # save execution plan in py file
    et.save_dump(out_filename=output_xlsx_filename)

def test_cycle():
    cr = hyper_etable.run_util.CycleRun(
        input_xlsx_filename='./tests/dump/dump_me.xlsx',
        input_py_filename='./tests/dump/gg.py',
        output_plan_filename='./tests/dump/plan.py',
        output_xlsx_filename='./tests/dump/result.xlsx',
        output_classes_filename='./tests/dump/classes_dump.py',
        has_header=False)
    for r in range(5):
        cr.cycle()
        cr.e_table.mod.DATA.DATA_79.D = 8
        cr.e_table.mod.DATA.GOAL= False