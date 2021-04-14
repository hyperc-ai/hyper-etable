from collections import defaultdict
import os.path
import schedula
from formulas.excel import ExcelModel, BOOK, ERR_CIRCULAR
from formulas.excel.xlreader import load_workbook
from formulas.functions import is_number
import formulas
import unidecode
import string
import hyperc.util
import hyperc.settings
import hyper_etable.etable_transpiler
import hyperc.xtj
import itertools

class ETable:
    def __init__(self, filename, project_name="my_project") -> None:
        self.filename = filename
        APPENDIX = hyperc.settings.APPENDIX
        hyperc.settings.APPENDIX = hyperc.xtj.str_to_py(filename) + "_" + project_name
        self.tempdir = hyperc.util.get_work_dir()
        hyperc.settings.APPENDIX = APPENDIX
        
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

        code = defaultdict(list)

        used_cell_set = set()

        for node_key, node_val in xl_mdl.dsp.dmap.nodes.items():
            if ('inputs' in node_val) and ('outputs' in node_val):
                assert len(node_val['outputs']) == 1, f'Currently support only one cell as output'
                output = node_val['outputs'][0]
                out_py = hyperc.xtj.str_to_py(output)
                code[out_py].append(f'def hct_{out_py}():')
                code[out_py].append(f'    #{node_key}')
                for used_cell in itertools.chain(node_val['inputs'].keys(), node_val['outputs']):
                    used_cell_set.add(used_cell)
                for input in node_val['inputs']:
                    cell = formulas.Parser().ast("="+list(formulas.Parser().ast(f'={input}')[1].compile().dsp.nodes.keys())[0].replace(" = -","=-"))[0][0].attr
                    letter = cell['c1'].lower()
                    number = cell['r1']
                    sheet_name = hyperc.xtj.str_to_py(f"[{cell['excel']}]{cell['sheet']}")
                    var_name = f'var_tbl_{sheet_name}__hct_direct_ref__{number}_{letter}'
                    code[out_py].append(f'    {var_name} = HCT_STATIC_OBJECT.{sheet_name}_{number}.{letter}')

                formula = hyper_etable.etable_transpiler.EtableTranspiler(node_val)
                transpiled_formula = formula.transpile_start()
                cell = formulas.Parser().ast("="+list(formulas.Parser().ast(f'={output}')[1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0][0].attr
                out_var = hyper_etable.etable_transpiler.get_var_from_cell(cell)
                code[out_py].append(f'    {out_var} = {transpiled_formula}')
                code[out_py].append(f'    # side effect with {out_var} shoul be added here')
            
            with open(f"{self.tempdir}/hpy_etable.py", "w+") as f:
                for func in code.values():
                    f.write('\n'.join(func))
                    f.write('\n')
 
        # xl_mdl.calculate()
        # # xl_mdl.add_book(self.link_filename)
        # xl_mdl.write(dirpath=os.path.dirname(__file__))
        # # xl_mdl.finish()
        # # xl_mdl.calculate()
        # # xl_mdl.dsp.dispatch()
        # print('Finished excel-model')


        # xl_mdl.calculate({"'[EXTRA.XLSX]EXTRA'!A1:B1": [[1, 1]]})

        # books = _res2books(xl_mdl.write(xl_mdl.books))

        # msg = '%sCompared overwritten results in %.2fs.\n' \
        #         '%sComparing fresh written results.'

        # res_book = _res2books(xl_mdl.write())
