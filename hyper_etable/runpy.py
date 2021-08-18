import sys
import hyper_etable.etable
import pathlib


def main():
    if len(sys.argv) < 4:
        print(f"USAGE: {sys.argv[0]} calculate|genclass|run_plan <main.xlsx> [<main.py> [<plan.py>]]")
        sys.exit(1)
    command = sys.argv[1]
    if command == "calculate":
        xlsx_file = sys.argv[2]
        py_file = sys.argv[3]
        print("Running files:", xlsx_file, py_file)
        xlsx_file = pathlib.Path(xlsx_file)
        project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
        et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
        et.open_dump(has_header=True, addition_python_files=[py_file])
        et.dump_py("xlsx_to_py")
        et.solver_call_simple_wo_exec()
        et.save_plan(exec_plan=True)
        outfile_path = et.save_dump(has_header=True)
        print("... done!")
        print("To open result, CTRL-Click here:", outfile_path)
    elif command == "genclass":
        xlsx_file = sys.argv[2]
        print("Generating classes from file:", xlsx_file)
        xlsx_file = pathlib.Path(xlsx_file)
        project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
        et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
        et.open_dump(has_header=True)
        et.dump_py("xlsx_to_py")
    elif command == "run_plan":
        xlsx_file = sys.argv[2]
        py_file = sys.argv[3] # be careful pass file with origin function(action) declarations
        py_plan_filename = sys.argv[4]
        print(f"Execute plan {py_plan_filename} for {xlsx_file}")
        project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
        et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
        et.open_dump(has_header=True, addition_python_files=[py_file])
        et.run_plan(py_plan_filename=py_plan_filename)
    else:
        print("Available commands: calculate, genclass")
        print("Command not recognized:", command)

if __name__ == '__main__':
    main()

