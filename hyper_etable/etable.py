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
import sys
import types
import copy
import collections

class TableElementMeta(type):
    @hyperc.util.side_effect_decorator
    def __str__(self):
        return self.__table_name__

class ETable:
    def __init__(self, filename, project_name="my_project") -> None:
        self.filename = filename
        APPENDIX = hyperc.settings.APPENDIX
        hyperc.settings.APPENDIX = hyperc.xtj.str_to_py(filename) + "_" + project_name
        self.tempdir = hyperc.util.get_work_dir()
        hyperc.settings.APPENDIX = APPENDIX
        self.session_name = "etable_mod"
        self.mod = types.ModuleType(self.session_name)
        globals()[self.session_name] = self.mod
        sys.modules[self.session_name] = self.mod
        self.classes = {}
        self.objects = collections.defaultdict(dict)
        
    def get_new_table(self, table_name):
        ThisTable = TableElementMeta(table_name, (object,), {'__table_name__': table_name})
        ThisTable.__annotations__ = {}
        ThisTable.__annotations__['__table_name__'] = str
        ThisTable.__touched_annotations__ = set()
        ThisTable.__annotations_type_set__ = defaultdict(set)
        self.mod.__dict__[table_name] = ThisTable
        self.classes[table_name] = ThisTable
        self.classes[table_name].__qualname__ = f"{self.session_name}.{table_name}"
        return ThisTable

    def calculate(self):
        
        xl_mdl = ExcelModel()
        xl_mdl.loads(self.filename)

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

                formula= hyper_etable.etable_transpiler.EtableTranspiler(
                    node_key, node_val['inputs'].keys(), output)
                transpiled_formula, xl_mdl.cells[output].value = formula.transpile_start()
                code[out_py].extend(formula.code)
                out_var = hyper_etable.etable_transpiler.get_var_from_cell(output)
                code[out_py].append(f'    {out_var} = {transpiled_formula}')
                code[out_py].append(f'    # side effect with {out_var} shoul be added here')
            
        with open(f"{self.tempdir}/hpy_etable.py", "w+") as f:
            for func in code.values():
                f.write('\n'.join(func))
                f.write('\n')

        py_table_name = hyperc.xtj.str_to_py(self.filename)

        ThisTable = self.get_new_table(py_table_name)

        for cell in used_cell_set:

            recid, letter = hyper_etable.etable_transpiler.split_cell(cell)
            if recid not in self.objects[py_table_name]:
                rec_obj = ThisTable()
                # rec_obj.__row_record__ = copy.copy(cell)
                rec_obj.__recid__ = recid
                # rec_obj.__table_name__ += f'!_{str(rec_obj.__recid__)} {",".join(map(str, rec.values()))}'
                rec_obj.__touched_annotations__ = set()
                # ThisTable.__annotations_type_set__ = defaultdict(set)
                self.objects[py_table_name][recid] = rec_obj
            self.objects[py_table_name][recid].__touched_annotations__.add(letter)
            # rec_obj.__annotations__.add(letter)
            if xl_mdl.cells[cell].value is not schedula.EMPTY:
                setattr(self.objects[py_table_name][recid], letter, xl_mdl.cells[cell].value)

        
        print("finish")
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
