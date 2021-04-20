from collections import defaultdict
import schedula
import formulas.excel
import formulas
import hyperc
import hyperc.util
import hyperc.settings
import hyper_etable.etable_transpiler
import hyperc.xtj
import itertools
import sys
import types
import collections

class TableElementMeta(type):
    @hyperc.util.side_effect_decorator
    def __str__(self):
        return self.__table_name__

def operator_name_to_operator(op):
    expand = {">": "greaterThan", ">=": "greaterThanOrEqual", "<": "lessThan", "<=": "lessThanOrEqual",
              "==": "equal", "!=": "notEqual"}
    for k, v in expand.items():
        if v == op:
            return k
    return None

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
        self.mod.side_effect = hyperc.side_effect
        self.mod.ensure_ne = hyperc.ensure_ne
        self.mod.StaticObject = type("StaticObject", (object, ), {})
        self.mod.StaticObject.__annotations__ = {}
        self.mod.StaticObject.__qualname__ = f"{self.session_name}.StaticObject"
        self.mod.HCT_STATIC_OBJECTS = self.mod.StaticObject()
        self.mod.HCT_OBJECTS = {}


        
    def get_new_table(self, table_name):
        ThisTable = TableElementMeta(table_name, (object,), {'__table_name__': table_name})
        ThisTable.__annotations__ = {}
        ThisTable.__annotations__['__table_name__'] = str
        ThisTable.__touched_annotations__ = set()
        ThisTable.__annotations_type_set__ = defaultdict(set)
        self.mod.__dict__[table_name] = ThisTable
        self.classes[table_name] = ThisTable
        self.classes[table_name].__qualname__ = f"{self.session_name}.{table_name}"
        self.mod.HCT_OBJECTS[table_name] = []
        return ThisTable

    def calculate(self):
        
        xl_mdl = formulas.excel.ExcelModel()
        xl_mdl.loads(self.filename)

        code = {}

        used_cell_set = set()

        for node_key, node_val in xl_mdl.dsp.dmap.nodes.items():
            if ('inputs' in node_val) and ('outputs' in node_val):
                assert len(node_val['outputs']) == 1, f'Currently support only one cell as output'
                output = node_val['outputs'][0]
                out_py = hyperc.xtj.str_to_py(output)
                code_init = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_{out_py}')
                code_init.init.append(f'    #{node_key}')
                for used_cell in itertools.chain(node_val['inputs'].keys(), node_val['outputs']):
                    used_cell_set.add(used_cell)
                for input in node_val['inputs']:
                    filename, sheet, recid, letter = hyper_etable.etable_transpiler.split_cell(input)
                    sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}")
                    var_name = f'var_tbl_{sheet_name}__hct_direct_ref__{recid}_{letter}'
                    code_init.init.append(f'    {var_name} = HCT_STATIC_OBJECT.{sheet_name}_{recid}.{letter}')

                # formula= hyper_etable.etable_transpiler.EtableTranspiler(
                #     node_key, node_val['inputs'].keys(), output)
                formula = hyper_etable.etable_transpiler.EtableTranspilerEasy(
                    node_key, node_val['inputs'].keys(), output, init_code=code_init)
                formula.transpile_start()
                # set default value for selectif
                xl_mdl.cells[output].value = formula.default
                code.update(formula.code)
        
        # look for mergable actions
        deleted_keys = set()
        for func_name_other in list(code.keys()):
            if func_name_other in deleted_keys:
                continue
            for s_c in code[func_name_other].selected_cell:
                for func_name in list(code.keys()):
                    if func_name_other in deleted_keys:
                        continue
                    if func_name == func_name_other:
                        continue
                    if s_c in code[func_name].selected_cell:
                        code[func_name].merge(code[func_name_other])

                        del code[func_name_other]
                        deleted_keys.add(func_name_other)


        s_code = ''
        fn = f"{self.tempdir}/hpy_etable.py"
        with open(fn, "w+") as f:
            for func in code.values():
                f.write(str(func))
                f.write('\n')
                s_code += str(func)
                s_code += '\n'

        f_code = compile(s_code, fn, 'exec')
 
        exec(f_code, self.mod.__dict__)
        functions = {}
        for func_code in code.values():
            functions[func_code.name] = self.mod.__dict__[func_code.name]
            functions[func_code.name].orig_source = str(func_code)

        for cell in used_cell_set:

            filename, sheet, recid, letter = hyper_etable.etable_transpiler.split_cell(cell)
            py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
            if recid not in self.objects[py_table_name]:
                if py_table_name not in self.classes:
                    ThisTable = self.get_new_table(py_table_name)
                else:
                    ThisTable = self.classes[py_table_name]
                # if 
                rec_obj = ThisTable()
                # rec_obj.__row_record__ = copy.copy(cell)
                rec_obj.__recid__ = recid
                rec_obj.__table_name__ += f'[{filename}]{sheet}_{recid}'
                rec_obj.__touched_annotations__ = set()
                # ThisTable.__annotations_type_set__ = defaultdict(set)
                self.objects[py_table_name][recid] = rec_obj
                self.mod.HCT_OBJECTS[py_table_name].append(rec_obj)
            self.objects[py_table_name][recid].__touched_annotations__.add(letter)
            #TODO add type detector
            self.classes[py_table_name].__annotations__[letter] = int
            # rec_obj.__annotations__.add(letter)
            if xl_mdl.cells[cell].value is not schedula.EMPTY:
                filename, sheet, recid, letter = hyper_etable.etable_transpiler.split_cell(cell)
                sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}") + f'_{recid}'
                if sheet_name not in self.mod.HCT_OBJECTS:
                    self.mod.HCT_OBJECTS[sheet_name] = []
                if self.objects[py_table_name][recid] not in self.mod.HCT_OBJECTS[sheet_name]:
                    setattr(self.mod.HCT_STATIC_OBJECTS, sheet_name, self.objects[py_table_name][recid])
                    self.mod.StaticObject.__annotations__[sheet_name] = self.classes[py_table_name]
                self.mod.HCT_OBJECTS[sheet_name].append(f'    {var_name} = HCT_STATIC_OBJECT.{sheet_name}.{letter}')
                setattr(self.objects[py_table_name][recid], letter, xl_mdl.cells[cell].value)

        for clsv in self.classes.values():
            init_f_code = []
            init_pars = []
            if hyperc.settings.DEBUG:
                print(f" {clsv} -  {clsv.__annotations__}")
            for par_name, par_type in clsv.__annotations__.items():
                if par_name == '__table_name__':
                    continue
                # Skip None type cell
                if par_type is None:
                    par_type = str
                    clsv.__annotations__[par_name] = str
                init_f_code.append(
                    f'self.{par_name} = hct_p_{par_name} # cell "{par_name.upper()}" of table "{clsv.__table_name__}"')
                if not par_type in hyperc.xtj.DEFAULT_VALS:
                    raise TypeError(f"Could not resolve type for {clsv.__name__}.{par_name} (forgot to init cell?)")
                init_pars.append(f"hct_p_{par_name}:{par_type.__name__}={hyperc.xtj.DEFAULT_VALS[par_type]}")
            if len(init_f_code) == 0:
                continue
            full_f_code = '\n    '.join(init_f_code)
            full_f_pars = ",".join(init_pars)
            full_code = f"def hct_f_init(self, {full_f_pars}):\n    {full_f_code}"
            fn = f"{self.tempdir}/hpy_init_{clsv.__name__}.py"
            open(fn, "w+").write(full_code)
            f_code = compile(full_code, fn, 'exec')
            exec(f_code, globals())
            clsv.__init__ = globals()["hct_f_init"]
            clsv.__init__.__name__ = "__init__"

        # Now generate init for static object
        init_f_code = []
        for attr_name, attr_type in self.mod.StaticObject.__annotations__.items():
            init_f_code.append(f"self.{attr_name} = HCT_STATIC_OBJECTS.{attr_name}")  # if it does not ignore, fix it!
        if init_f_code:
            HCT_STATIC_OBJECTS = self.mod.HCT_STATIC_OBJECTS
            full_f_code = '\n    '.join(init_f_code)
            full_code = f"def hct_stf_init(self):\n    {full_f_code}"
            fn = f"{self.tempdir}/hpy_stf_init_{self.mod.StaticObject.__name__}.py"
            open(fn, "w+").write(full_code)
            f_code = compile(full_code, fn, 'exec')
            exec(f_code, self.mod.__dict__)
            self.mod.StaticObject.__init__ = self.mod.__dict__["hct_stf_init"]
            self.mod.StaticObject.__init__.__name__ = "__init__"

        # Collect conditional formatting
        # TODO set goal here 
        goal_code = defaultdict(list)
        for filename, book in xl_mdl.books.items():
            for worksheet in book[formulas.excel.BOOK].worksheets:
                for rule_cell in worksheet.conditional_formatting._cf_rules:
                    assert len(rule_cell.sqref.ranges) == 1, "only one cell ondition support"
                    sheet = worksheet.title
                    cell = f"'[{filename}]{sheet}'!{rule_cell.sqref.ranges[0].coord}"
                    filename, sheet, recid, letter = hyper_etable.etable_transpiler.split_cell(cell)
                    sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}") + f'_{recid}'
                    for rule in rule_cell.rules:
                        value = hyper_etable.etable_transpiler.formulas_parser(rule.formula[0])[0]
                        if isinstance(value, formulas.tokens.operand.Range):
                            filename_value, sheet_value, recid_value, letter_value = hyper_etable.etable_transpiler.split_cell(rule.formula[0])
                            if filename_value == '':
                                filename_value = filename
                            if sheet_value == '':
                                sheet_value = sheet
                            sheet_name_value = hyperc.xtj.str_to_py(f"[{filename_value}]{sheet_value}") + f'_{recid_value}'
                            goal_code[cell].append(
                                f'    assert HCT_STATIC_OBJECT.{sheet_name}_{recid}.{letter} {operator_name_to_operator(rule.operator)} HCT_STATIC_OBJECT.{sheet_name_value}_{recid_value}.{letter_value}')
                        elif isinstance(value, formulas.tokens.operand.Number):
                            goal_code[cell].append(
                                f'    assert HCT_STATIC_OBJECT.{sheet_name}_{recid}.{letter} {operator_name_to_operator(rule.operator)} {int(value.attr["name"])}')
                        elif isinstance(value, formulas.tokens.operand.String):
                            goal_code[cell].append(
                                f'    assert HCT_STATIC_OBJECT.{sheet_name}_{recid}.{letter} {operator_name_to_operator(rule.operator)} {value.attr["name"]}')





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
