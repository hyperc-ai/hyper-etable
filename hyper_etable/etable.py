from hyperc import solve
import hyperc.poc_symex
import schedula
from formulas.excel import ExcelModel, BOOK, ERR_CIRCULAR
from formulas.excel.xlreader import load_workbook
from formulas.functions import is_number

BOOK = schedula.Token('Book')
def _book2dict(book):
    res = {}
    for ws in book.worksheets:
        s = res[ws.title.upper()] = {}
        for k, cell in ws._cells.items():
            value = getattr(cell, 'value', None)
            if value is not None:
                s[cell.coordinate] = value
    return res


def _res2books(res):
    return {k.upper(): _book2dict(v[BOOK]) for k, v in res.items()}



class ETable:
    def __init__(self, filename) -> None:
        self.filename = filename
        
    def calculate(self):
        xl_mdl = ExcelModel()
        xl_mdl.loads(self.filename)
        # for book in xl_mdl.books.values():
        #     for coord in list(book.values())[0].active._cells:
        #         # book.Book.active._cells[coord] = 99
        #         list(book.values())[0].active._cells[coord].value = 99

        # for coord in xl_mdl.cells:
        #     if xl_mdl.cells[coord].value is not schedula.EMPTY:
        #     #    xl_mdl.cells[coord].value = 44
        #     #    xl_mdl.dsp.default_values[coord]['value'] = 66
        #        xl_mdl.dsp.default_values[coord]['value'] = hyperc.poc_symex.HCProxy(
        #            wrapped=xl_mdl.cells[coord].value, name=coord, parent=None, place_id="__STATIC")

        xl_mdl.calculate()
        # xl_mdl.add_book(self.link_filename)
        xl_mdl.write(dirpath=os.path.dirname(__file__))
        # xl_mdl.finish()
        # xl_mdl.calculate()
        # xl_mdl.dsp.dispatch()
        print('Finished excel-model')


        # xl_mdl.calculate({"'[EXTRA.XLSX]EXTRA'!A1:B1": [[1, 1]]})

        # books = _res2books(xl_mdl.write(xl_mdl.books))

        # msg = '%sCompared overwritten results in %.2fs.\n' \
        #         '%sComparing fresh written results.'

        # res_book = _res2books(xl_mdl.write())


if __name__ == "__main__":
    import os.path
    mydir = os.path.dirname(__file__)
    # file='trucks.xlsx'
    # file='summm.xlsx'
    file = 'plus.xlsx'
    et = ETable(os.path.join(mydir, file))
    et.calculate()
