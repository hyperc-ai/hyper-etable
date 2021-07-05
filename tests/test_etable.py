"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import os

def test_etable():
    mydir = os.path.dirname(__file__)
    file = 'a_sfr_double.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "watchtakeif")
    et.calculate()
