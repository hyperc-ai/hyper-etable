"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import os
import pytest
import pathlib

@pytest.mark.timeout(300)
@pytest.mark.parametrize('name, xlsx_file', [(str(p), p) for p in pathlib.Path('./tests/xlsx/').rglob('*.xlsx')])
def test_solve_xtj(name, xlsx_file):
    print(f"\ntest file {xlsx_file}", end='')
    project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
    et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
    et.calculate()

