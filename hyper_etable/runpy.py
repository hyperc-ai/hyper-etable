import sys
import hyper_etable.etable
import pathlib
import os

command = sys.argv[1]
if command == "calcbase":
    input_db = sys.argv[2]
    py_file = sys.argv[3]
    output_classes_filename='_class.py'
    output_plan_file = '_plan.py'
    et = hyper_etable.etable.ETable(project_name='calcbase')
    db_connector = et.open_from(path=input_db, has_header=True, proto='sqlalchemy', addition_python_files=[py_file])
    et.dump_py(out_filename=output_classes_filename) # save classes in py file
    et.solver_call_plan_n_exec() # solve with execution in pddl.py
    et.save_plan(prefix='et.mod.DATA.', out_filename=output_plan_file) # save execution plan in py file
    
    db_connector.save()
if command == "calculate":
    xlsx_file = sys.argv[2]
    py_file = sys.argv[3]
    has_header = True
    print("Running files:", xlsx_file, py_file)
    xlsx_file = pathlib.Path(xlsx_file)
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(project_name=project_name)
    connector = et.open_from(path=xlsx_file,
                             has_header=True, proto='xlsx', addition_python_files=[py_file])
    et.dump_py("xlsx_to_py")
    et.solver_call_simple_wo_exec()
    et.save_plan(exec_plan=True)
    output_xlsx_filename = pathlib.Path(os.path.join(xlsx_file.parent, f'out_{xlsx_file.name}'))
    connector.save_all(out_path=output_xlsx_filename)
    print("... done!")
    print("To open result, CTRL-Click here:", output_xlsx_filename)
elif command == "genclass":
    xlsx_file = sys.argv[2]
    print("Generating classes from file:", xlsx_file)
    xlsx_file = pathlib.Path(xlsx_file)
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(project_name=project_name)
    et.open_from(path=xlsx_file, proto='xlsx', has_header=True)
    et.dump_py("xlsx_to_py")
elif command == "run_plan":
    xlsx_file = sys.argv[2]
    py_file = sys.argv[3] # be careful pass file with origin function(action) declarations
    py_plan_filename = sys.argv[4]
    print(f"Execute plan {py_plan_filename} for {xlsx_file}")
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(project_name=project_name)
    et.open_from(path=xlsx_file, has_header=True, addition_python_files=[py_file])
    et.run_plan(py_plan_filename=py_plan_filename)
else:
    print("Available commands: calculate, genclass")
    print("Command not recognized:", command)
