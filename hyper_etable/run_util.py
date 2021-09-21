import hyper_etable.etable
import pathlib
import shutil
import os
from typing import List

def run_gui(files:List):
    """files is list of triples (path, protocol)"""
    
    assert len(files) > 0 , "must have at least one file"

    #detect header
    et = hyper_etable.etable.ETable(project_name = "run_gui")
    for conn_args in [files]:
        path, proto = conn_args
        conn = hyper_etable.connector.new_connector(path, proto, et.mod)
        raw_table = conn.get_raw_table()
        for table in raw_table.values():
            assert 1 in table, "table must have Header"


    if len(files)==1:
        path, proto = files[0]
        print("run ", path, proto)
    if len(files)>1:
        et = hyper_etable.etable.ETable(project_name = "run_gui")
        for conn_args in [files[0], files[-1]]:
            path, proto = conn_args
            if proto.lower() == 'msapi':
                conn = hyper_etable.connector.MSAPIConnector(path, et.mod, has_header=True)
            elif proto.lower() == 'gsheet':
                conn = hyper_etable.connector.GSheetConnector(path, et.mod, has_header=True)
            elif proto.lower() == 'xlsx':
                conn = hyper_etable.connector.XLSXConnector(path, et.mod, has_header=True)
            elif proto.lower() == 'airtable':
                conn = hyper_etable.connector.AirtableConnector(path, et.mod, has_header=True)
            if conn is None:
                raise ValueError(f'{proto} is not support')
        
            
        



def run(
  input_xlsx_filename:     str,
  input_py_filename:       str,
  output_classes_filename: str,
  output_plan_filename:    str,
  output_xlsx_filename:    str,
  has_header:bool = True, 
  input_classes_filename = None
  ):
    if input_classes_filename is None:
        input_classes_filename = output_classes_filename
    project_name = pathlib.Path(input_xlsx_filename).name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(input_xlsx_filename, project_name=project_name)
    et.open_dump(has_header=has_header, addition_python_files=[input_py_filename], external_classes_filename=input_classes_filename)
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
    et.open_dump(has_header=has_header, addition_python_files=[input_py_filename], external_classes_filename=output_classes_filename)
    et.dump_py(out_filename=output_classes_filename) # save classes in py file
    et.solver_call_plan_n_exec()  # solve with execution
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
        self.e_table.open_dump(has_header=has_header, addition_python_files=[input_py_filename], external_classes_filename=output_classes_filename)
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
        self.e_table.solver_call_plan_n_exec()  # solve with execution
        self.e_table.load_rows_in_table()
        self.e_table.save_plan(prefix='DATA.', out_filename=self.output_plan_filename) # save execution plan in py file
        self.e_table.save_dump(out_filename=self.output_xlsx_filename)