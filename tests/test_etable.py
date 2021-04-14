import hyperc.etable
import os

def test_etable():
    mydir = os.path.dirname(__file__)
    # file='trucks.xlsx'
    # file='summm.xlsx'
    # file = 'plus.xlsx'
    file = 'plus_selectif.xlsx'

    et = hyperc.etable.ETable(os.path.join(mydir, file), "test_etable")
    et.calculate()
