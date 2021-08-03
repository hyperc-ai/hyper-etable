import hyper_etable.run_util
import hyper_etable.etable
import pathlib

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