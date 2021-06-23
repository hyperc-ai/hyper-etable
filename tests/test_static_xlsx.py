"""PYTEST_DONT_REWRITE"""
import hyper_etable.etable
import os


def test_simpleinc_and_3_watch():
    mydir = os.path.dirname(__file__)
    file = 'static_xlsx/simpleinc_and_3_watch.xlsm'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "watchtakeif")
    et.calculate()
    et.finish()

    assert et.mod.HCT_STATIC_OBJECT.SIMPLEINC_AND_3_WATCH_XLSM_SHEET1_2.c == 1
    assert et.mod.HCT_STATIC_OBJECT.SIMPLEINC_AND_3_WATCH_XLSM_SHEET1_3.c == 2
    assert et.mod.HCT_STATIC_OBJECT.SIMPLEINC_AND_3_WATCH_XLSM_SHEET1_4.c == 3
    assert et.mod.HCT_STATIC_OBJECT.SIMPLEINC_AND_3_WATCH_XLSM_SHEET1_1.a == 5


