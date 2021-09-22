"""PYTEST_DONT_REWRITE"""
import hyper_etable.run_util
import pathlib

def test_dump():
    file1=pathlib.Path('./tests/gui1.xlsx')
    file2=pathlib.Path('./tests/gui2.xlsx')
    file2_bad=pathlib.Path('./tests/gui2_bad.xlsx')
    hyper_etable.run_util.run_gui([[file1,'xlsx'],[file2,'xlsx']])
    ok = True
    try:
        hyper_etable.run_util.run_gui([[file1,'xlsx'],[file2_bad,'xlsx']])
        ok = False
    except :
        pass
    assert ok, "Bad file should be exception raise"