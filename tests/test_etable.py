"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import os

def test_etable():
    mydir = os.path.dirname(__file__)
    file = 'xlsx/selectfromrange_takeif_twice_synced.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "selectfromrange_selectif_twice_synced")
    et.calculate()
