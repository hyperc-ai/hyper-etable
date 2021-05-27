"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import os

def test_etable():
    mydir = os.path.dirname(__file__)
    file = 'HyperC_test_2-1.bug.object.has.not.attribute.f_or.-.Copy.xlsm'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "watchtakeif")
    et.calculate()
