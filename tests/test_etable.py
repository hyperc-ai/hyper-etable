import hyper_etable.etable
import os

def test_etable():
    mydir = os.path.dirname(__file__)
    # file='trucks.xlsx'
    # file='summm.xlsx'
    # file = 'plus.xlsx'
    # file = 'simple_branch.xlsx'
    file = 'simple.xlsx'

    et = hyper_etable.etable.ETable(os.path.join(mydir, file), "test_etable")
    et.calculate()
