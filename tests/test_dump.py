import hyper_etable.etable
import itertools
import pytest
import pathlib
import glob
import os


def test_dump():
    xlsx_file='./tests/dump/dump_me.xlsx'
    xlsx_file = pathlib.Path(xlsx_file)
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.solve_dump()
    et.save_dump()
    
def test_doctor():
    xlsx_file='./tests/doctor/Doctor shifts schedulling - new.xlsx'
    xlsx_file = pathlib.Path(xlsx_file)
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.solve_dump()

def test_header():
    xlsx_file='./tests/header_select/has_header.xlsx'
    xlsx_file = pathlib.Path(xlsx_file)
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.open_dump(has_header=True)
    et.solver_call_simple_wo_exec()
    et.save_plan(exec_plan=False)
    et.save_dump(has_header=True)

def test_dentist():
    xlsx_file='./tests/dentist/dentists3.xlsx'
    xlsx_file = pathlib.Path(xlsx_file)
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.solve_dump(has_header=True)
    et.save_dump(has_header=True)


def test_space():
    xlsx_file='./tests/space_bug/Untitled 1.xlsx'
    xlsx_file = pathlib.Path(xlsx_file)
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.solve_dump()
    # et.save_dump()