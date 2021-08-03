import hyper_etable.etable

    
def open_test_solve_save_run(input_xlsx, input_py, output_dir_classes, output_dir_plan, output_dir_solution, project_name="etable_project", py_plan_prefix='DATA.', has_header=True):
    et = hyper_etable.etable.ETable(input_xlsx, project_name=project_name)
    et.open_dump(has_header=has_header, addition_python_files=input_py)
    et.dump_py(dir=output_dir_classes)
    et.solver_call_simple_with_exec()
    et.reset_data()
    et.solver_call_simple_wo_exec()
    et.save_plan(prefix=py_plan_prefix, out_dir=output_dir_plan)
    et.run_plan(et.plan_file)
    et.save_dump(out_dir=output_dir_solution)
