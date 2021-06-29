"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import itertools
import pytest
import pathlib
import glob
import os

try:
    @pytest.mark.timeout(3000)
    @pytest.mark.parametrize('name, xlsx_file',
                             [(str(p),
                               p)
                              for p in itertools.chain(
                                  *[glob.glob(os.path.join('./tests/', e)) for e in ('*.xlsm', '*.xlsx', '*.xlsx.txt', '*.xlsx.txt')])])
    def test_fast(name, xlsx_file):
        xlsx_file = pathlib.Path(xlsx_file)
        print(f"\ntest file {xlsx_file}", end='')
        project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
        et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
        et.calculate()
        et.finish()
except:
    pass

try:
    @pytest.mark.timeout(3000)
    @pytest.mark.parametrize('name, xlsx_file',
                             [(str(p),
                               p)
                              for p in itertools.chain(
                                  *[glob.glob(os.path.join('./tests/', e)) for e in ('*.xlsm', '*.xlsx', '*.xlsx.txt', '*.xlsx.txt')])])
    def test_fast_wo_precalc(name, xlsx_file):
        xlsx_file = pathlib.Path(xlsx_file)
        print(f"\ntest file {xlsx_file}", end='')
        project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
        et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
        et.enable_precalculation = False
        et.calculate()
        et.finish()
except:
    pass

try:
    @pytest.mark.timeout(3000)
    @pytest.mark.parametrize('name, xlsx_file',
                             [(str(p),
                               p)
                              for p in itertools.chain(
                                  *[glob.glob(os.path.join('./tests/xlsx/', e)) for e in ('*.xlsm', '*.xlsx', '*.xlsx.txt', '*.xlsx.txt')])])
    def test_fast_xslx_wo_precalc(name, xlsx_file):
        xlsx_file = pathlib.Path(xlsx_file)
        print(f"\ntest file {xlsx_file}", end='')
        project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
        et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
        et.enable_precalculation = False
        et.calculate()
        et.finish()
except:
    pass