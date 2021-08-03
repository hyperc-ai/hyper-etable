import hyper_etable.run_util
import hyper_etable.etable
import pathlib

def test_header():
    xlsx_file=pathlib.Path('./tests/basic/main.xlsx')
    out_dir = pathlib.Path('./tests/basic/out/')
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    hyper_etable.run_util.open_test_solve_save_run(
        input_xlsx=[xlsx_file],
        input_py=['./tests/basic/main.py'],
        output_dir_classes=out_dir,
        output_dir_plan=out_dir,
        output_dir_solution=out_dir,
        project_name=project_name,
        has_header=True)
    ADDITIONAL_RUNS = 2
    xlsx_file=pathlib.Path('./tests/basic/out/main.xlsx')
    for i in range(ADDITIONAL_RUNS):
        print("Loading next run", i)
        hyper_etable.run_util.open_test_solve_save_run(
            input_xlsx=[xlsx_file],
            input_py=['./tests/basic/main.py'],
            output_dir_classes=out_dir,
            output_dir_plan=out_dir,
            output_dir_solution=out_dir,
            project_name=project_name,
            has_header=True)
