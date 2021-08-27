import hyper_etable.etable
import pathlib
import shutil
import os

def run(
  input_xlsx_filename:     str,
  input_py_filename:       str,
  output_classes_filename: str,
  output_plan_filename:    str,
  output_xlsx_filename:    str,
  has_header:bool=True
  ):
    project_name = pathlib.Path(input_xlsx_filename).name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(input_xlsx_filename, project_name=project_name)
    et.open_dump(has_header=has_header, addition_python_files=[input_py_filename])
    # et.load_external_classes(output_classes_filename)
    et.dump_py(out_filename=output_classes_filename) # save classes in py file
    et.solver_call_plan_n_exec() # solve with execution in pddl.py
    et.load_rows_in_table()
    et.save_plan(prefix='DATA.', out_filename=output_plan_filename) # save execution plan in py file
    et.save_dump(out_filename=output_xlsx_filename)

def simple_run(
  input_xlsx_filename:     str,
  input_py_filename:       str,
  output_classes_filename: str,
  output_xlsx_filename:    str,
  has_header:bool=True
  ):
    project_name = pathlib.Path(input_xlsx_filename).name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(input_xlsx_filename, project_name=project_name)
    et.open_dump(has_header=has_header, addition_python_files=[input_py_filename])
    et.dump_py(out_filename=output_classes_filename) # save classes in py file
    et.solver_call_plan_n_exec()  # solve without execution
    et.load_rows_in_table()
    et.save_dump(out_filename=output_xlsx_filename)

class CycleRun:
    def __init__(self,
    input_xlsx_filename:     str,
    input_py_filename:       str,
    output_classes_filename: str,
    output_plan_filename:    str,
    output_xlsx_filename:    str,
    has_header:bool=True
    ):
        self.first_run = True
        self.run_counter = 1
        self.input_xlsx_filename = input_xlsx_filename
        self.input_py_filename = input_py_filename
        self.output_classes_filename = pathlib.Path(output_classes_filename)
        self.output_classes_filename.parent.mkdir(parents=True, exist_ok=True)
        self.output_xlsx_filename = output_xlsx_filename
        self.output_xlsx_filename_origin = pathlib.Path(output_xlsx_filename)
        self.output_xlsx_filename_origin.parent.mkdir(parents=True, exist_ok=True)
        self.output_plan_filename = output_plan_filename
        self.output_plan_filename_origin = pathlib.Path(output_plan_filename)
        self.output_plan_filename_origin.parent.mkdir(parents=True, exist_ok=True)
        project_name = pathlib.Path(input_xlsx_filename).name.replace("/", "_").replace(".", "_")
        self.e_table = hyper_etable.etable.ETable(input_xlsx_filename, project_name=project_name)
        self.e_table.open_dump(has_header=has_header, addition_python_files=[input_py_filename])
        self.e_table.dump_py(out_filename=output_classes_filename) # save classes in py file
        

    def cycle(self):
        if self.first_run:
            self.first_run = False
        else:
            if self.run_counter == 1:
                output_xlsx_filename_was = self.output_xlsx_filename
                output_plan_filename_was = self.output_plan_filename
                self.output_xlsx_filename = pathlib.Path(os.path.join(self.output_xlsx_filename_origin.parent, f'0_{self.output_xlsx_filename_origin.name}'))
                self.output_plan_filename = pathlib.Path(os.path.join(self.output_plan_filename_origin.parent, f'0_{self.output_plan_filename_origin.name}'))
                shutil.move(output_xlsx_filename_was, self.output_xlsx_filename)
                shutil.move(output_plan_filename_was, self.output_plan_filename)
            self.output_xlsx_filename = pathlib.Path(os.path.join(self.output_xlsx_filename_origin.parent, f'{self.run_counter}_{self.output_xlsx_filename_origin.name}'))
            self.output_plan_filename = pathlib.Path(os.path.join(self.output_plan_filename_origin.parent, f'{self.run_counter}_{self.output_plan_filename_origin.name}'))
            self.run_counter += 1
        self.e_table.solver_call_simple_wo_exec()  # solve without execution
        self.e_table.save_plan(prefix='DATA.', out_filename=self.output_plan_filename) # save execution plan in py file
        self.e_table.run_plan(self.output_plan_filename)
        self.e_table.save_dump(out_filename=self.output_xlsx_filename)