import sys
import hyper_etable.etable
import pathlib

command = sys.argv[1]
if command == "calcbase":
    input_db = sys.argv[2]
    py_file = sys.argv[3]
    input_py_filename=py_file
    output_classes_filename='_class.py'
    output_plan_file = '_plan.py'
    et = hyper_etable.etable.ETable(project_name='calcbase')
    db_connector = et.open_from(path=input_db, has_header=True, proto='sqlalchemy', addition_python_files=[input_py_filename])
    et.dump_py(out_filename=output_classes_filename) # save classes in py file
    et.solver_call_plan_n_exec() # solve with execution in pddl.py
    et.save_plan(prefix='et.mod.DATA.', out_filename=output_plan_file) # save execution plan in py file
    
    db_connector.save()
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