"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import itertools
import pytest
import pathlib

try:
    @pytest.mark.timeout(300)
    @pytest.mark.parametrize('name, xlsx_file',
                             [(str(p),
                               p)
                              for p in itertools.chain(
                                  *[pathlib.Path('./tests/').rglob(e) for e in ('*.xlsm', '*.xlsx', '*.xlsx.txt', '*.xlsx.txt')])])
    def test_fast(name, xlsx_file):
        print(f"\ntest file {xlsx_file}", end='')
        project_name = xlsx_file.name.replace("/", "_").replace(".", "_")
        et = hyper_etable.etable.ETable(xlsx_file, project_name=project_name)
        et.calculate()
except:
    pass
