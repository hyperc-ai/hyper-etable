"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import os

def test_etable():
    mydir = os.path.dirname(__file__)
    file = 'selectfromrange.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "selectfromrange")
    et.calculate()


def test_selectif_double():
    mydir = os.path.dirname(__file__)
    file = 'selectif_double.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "selectif_double")
    et.calculate()


def test_selectfromrange_selectif_twice():
    mydir = os.path.dirname(__file__)
    file = 'selectfromrange_selectif_twice.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "selectfromrange_selectif_twice")
    et.calculate()


def test_selectfromrange_selectif_twice():
    mydir = os.path.dirname(__file__)
    file = 'selectfromrange_selectif_twice_synced.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "selectfromrange_selectif_twice_synced")
    et.calculate()


def test_selectfromrange_from_select():
    mydir = os.path.dirname(__file__)
    file = 'selectfromrange_from_select.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "selectfromrange_from_select")
    et.calculate()


def test_aformula():
    mydir = os.path.dirname(__file__)
    file = 'xlsx/takeif_aformula.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "aformula")
    et.calculate()

def test_selectfromrange_from_select2():
    mydir = os.path.dirname(__file__)
    file = 'xlsx/selectfromrange_from_select.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "selectfromrange_from_select")
    et.calculate()
