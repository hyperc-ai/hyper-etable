import hyper_etable.run_util
import hyper_etable.etable
import pathlib


def open_test_solve_save_run(input_xlsx, input_py, output_dir_classes, output_dir_plan, output_dir_solution, project_name="etable_project", py_plan_prefix='DATA.', has_header=True):
    """test for hyper_etable.run_util.open_test_solve_save_run"""
    et = hyper_etable.etable.ETable(input_xlsx, project_name=project_name)
    et.open_dump(has_header=has_header, addition_python_files=input_py)
    et.dump_py(dir=output_dir_classes)
    assert et.mod.DATA.DATA_79.D == 8
    et.solver_call_simple_with_exec()
    assert et.mod.DATA.DATA_79.D == 5
    et.reset_data()
    assert et.mod.DATA.DATA_79.D == 8
    et.solver_call_simple_wo_exec()
    assert et.mod.DATA.DATA_79.D == 8
    et.save_plan(prefix=py_plan_prefix, out_dir=output_dir_plan)
    assert et.mod.DATA.DATA_79.D == 8
    et.run_plan(et.plan_file)
    assert et.mod.DATA.DATA_79.D == 5
    et.save_dump(out_dir=output_dir_solution)
    assert et.mod.DATA.DATA_79.D == 5

def test_dump():
    xlsx_file=pathlib.Path('./tests/dump/dump_me.xlsx')
    out_dir = pathlib.Path('./tests/dump/out/')
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    # hyper_etable.run_util.open_test_solve_save_run(
    open_test_solve_save_run(
        input_xlsx=[xlsx_file],
        input_py=['./tests/dump/gg.py'],
        output_dir_classes=out_dir,
        output_dir_plan=out_dir,
        output_dir_solution=out_dir,
        project_name=project_name,
        has_header=False)

def test_dump():
    xlsx_file=pathlib.Path('./tests/dump/dump_me.xlsx')
    out_dir = pathlib.Path('./tests/dump/out/')
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    hyper_etable.run_util.open_test_solve_save_run(
        input_xlsx=[xlsx_file],
        input_py=['./tests/dump/gg.py'],
        output_dir_classes=out_dir,
        output_dir_plan=out_dir,
        output_dir_solution=out_dir,
        project_name=project_name,
        has_header=False)

def test_header():
    xlsx_file=pathlib.Path('./tests/header_select/data.xlsx')
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable([xlsx_file], project_name=project_name)
    et.open_dump(has_header=True, addition_python_files=['./tests/header_select/a.py'])
    et.generate_invariants()
    et.dump_py()
    # et.solver_call_simple_wo_exec()
    # et.save_plan(exec_plan=True)
    # et.save_dump(has_header=True)

def test_space():
    xlsx_file='./tests/space_bug/Untitled 1.xlsx'
    xlsx_file = pathlib.Path(xlsx_file)
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.solve_dump()
    # et.save_dump()