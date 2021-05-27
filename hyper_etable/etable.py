from collections import defaultdict
from os import mkdir
import schedula
import formulas.excel
import formulas
import hyperc
import hyperc.util
import hyperc.settings
import hyper_etable.etable_transpiler
import hyper_etable.spiletrancer
import hyperc.xtj
import itertools
import sys
import time
import types
import collections
import copy
import os.path
import pathlib
import openpyxl


def stack_code_gen_old(obj_name):
    declare = []
    add = []
    drop = []
    init = []
    for i in range(5):
        #init
        init.append(f'self.row{i}_not_hasattr = True')

        #declare
        declare.append(f'row{i}: {obj_name}')
        declare.append(f'row{i}_letter: str')
        declare.append(f'row{i}_not_hasattr: bool')

        #def add(self, obj: Sheet1, letter: str)
        if i == 0:
            add.append(f'if static_stack_sheet.row{i}_not_hasattr == True:')
        else:
            add.append(f'elif static_stack_sheet.row{i}_not_hasattr == True:')
        add.append(f'    static_stack_sheet.row{i} = obj')
        add.append(f'    static_stack_sheet.row{i}_letter = letter')
        add.append(f'    static_stack_sheet.row{i}_not_hasattr = False')

        # def drop(self):
        drop.append(f'static_stack_sheet.row{i}_not_hasattr = True')

    declare = "\n    ".join(declare)
    init = '\n        '.join(init)
    add = '\n    '.join(add)
    drop = '\n    '.join(drop)

    return f'''
class StaticStackSheet:
    {declare}

    def __init__(self):
        {init}

static_stack_sheet = StaticStackSheet()

def stack_add(obj: {obj_name}, letter: str):
    {add}

def stack_drop():
    {drop}

'''


stack_code_gen = lambda cls_name: f"""

NONE_ROW_0 = {cls_name}()
NONE_ROW_1 = {cls_name}()
NONE_ROW_2 = {cls_name}()
NONE_ROW_3 = {cls_name}()
NONE_ROW_4 = {cls_name}()

class StaticStackSheet:
    row0: {cls_name}
    row0_letter: str
    row0_not_hasattr: bool
    row1: {cls_name}
    row1_letter: str
    row1_not_hasattr: bool
    row2: {cls_name}
    row2_letter: str
    row2_not_hasattr: bool
    row3: {cls_name}
    row3_letter: str
    row3_not_hasattr: bool
    row4: {cls_name}
    row4_letter: str
    row4_not_hasattr: bool

    def __init__(self):
        self.row0_not_hasattr = True
        self.row1_not_hasattr = True
        self.row2_not_hasattr = True
        self.row3_not_hasattr = True
        self.row4_not_hasattr = True
        self.row0_letter = ""
        self.row1_letter = ""
        self.row2_letter = ""
        self.row3_letter = ""
        self.row4_letter = ""
        self.row0 = NONE_ROW_0
        self.row1 = NONE_ROW_1
        self.row2 = NONE_ROW_2
        self.row3 = NONE_ROW_3
        self.row4 = NONE_ROW_4


static_stack_sheet = StaticStackSheet()


#@not_planned
def _drop_letter(obj, letter):  # underscore functions don't get planned
    if letter == "a":
        obj.a_not_hasattr = True
    elif letter == "b":
        obj.b_not_hasattr = True
    elif letter == "c":
        obj.c_not_hasattr = True


def _stack_add(obj: {cls_name}, letter: str):
    if static_stack_sheet.row0_not_hasattr == True:
        static_stack_sheet.row0 = obj
        static_stack_sheet.row0_letter = letter
        static_stack_sheet.row0_not_hasattr = False
    elif static_stack_sheet.row1_not_hasattr == True:
        static_stack_sheet.row1 = obj
        static_stack_sheet.row1_letter = letter
        static_stack_sheet.row1_not_hasattr = False
#    elif static_stack_sheet.row2_not_hasattr == True:
#        static_stack_sheet.row2 = obj
#        static_stack_sheet.row2_letter = letter
#        static_stack_sheet.row2_not_hasattr = False
#    elif static_stack_sheet.row3_not_hasattr == True:
#        static_stack_sheet.row3 = obj
#        static_stack_sheet.row3_letter = letter
#        static_stack_sheet.row3_not_hasattr = False
#    elif static_stack_sheet.row4_not_hasattr == True:
#        static_stack_sheet.row4 = obj
#        static_stack_sheet.row4_letter = letter
#        static_stack_sheet.row4_not_hasattr = False

def _stack_drop():
    static_stack_sheet.row0_not_hasattr = True
    static_stack_sheet.row1_not_hasattr = True
    static_stack_sheet.row2_not_hasattr = True
    static_stack_sheet.row3_not_hasattr = True
    static_stack_sheet.row4_not_hasattr = True
    assert static_stack_sheet.row0 != static_stack_sheet.row1
    #assert static_stack_sheet.row0 != static_stack_sheet.row2
    #assert static_stack_sheet.row0 != static_stack_sheet.row3
    #assert static_stack_sheet.row0 != static_stack_sheet.row4
    #assert static_stack_sheet.row1 != static_stack_sheet.row2
    #assert static_stack_sheet.row1 != static_stack_sheet.row3
    #assert static_stack_sheet.row1 != static_stack_sheet.row4
    #assert static_stack_sheet.row2 != static_stack_sheet.row3
    #assert static_stack_sheet.row2 != static_stack_sheet.row4
    #assert static_stack_sheet.row3 != static_stack_sheet.row4
    if static_stack_sheet.row0_letter != "":
        _drop_letter(static_stack_sheet.row0, static_stack_sheet.row0_letter)
        static_stack_sheet.row0_letter = ""
    if static_stack_sheet.row1_letter != "":
        _drop_letter(static_stack_sheet.row1, static_stack_sheet.row1_letter)
        static_stack_sheet.row1_letter = ""
#    if static_stack_sheet.row2_letter != "":
#        _drop_letter(static_stack_sheet.row2, static_stack_sheet.row2_letter)
#        static_stack_sheet.row2_letter = ""
#    if static_stack_sheet.row3_letter != "":
#        _drop_letter(static_stack_sheet.row3, static_stack_sheet.row3_letter)
#        static_stack_sheet.row3_letter = ""
#    if static_stack_sheet.row4_letter != "":
#        _drop_letter(static_stack_sheet.row4, static_stack_sheet.row4_letter)
#        static_stack_sheet.row4_letter = ""


# def _stack_drop():
    # pass

"""

def stack_code_gen_all(objects):
    l_all_hasattr_drop = []
    for cname, rows in objects.items():
        for idx, rowobj in rows.items():
            colnames = type(rowobj).__annotations__.keys()
            for col in colnames:
                if col.startswith("_"): continue
                if len(col) > 4: continue
                # if not "not_hasattr" in col: continue
                if not hasattr(rowobj, col): continue
                if getattr(rowobj, f"{col}_not_hasattr") == False: continue
                l_all_hasattr_drop.append(f"HCT_STATIC_OBJECT.{cname}_{idx}.{col}_not_hasattr = True")

    drop_content = "\n    ".join(l_all_hasattr_drop)
    scode = f"""def _stack_drop():
    pass
    {drop_content}"""
    return scode

class TableElementMeta(type):
    @hyperc.util.side_effect_decorator
    def __str__(self):
        return self.__table_name__
    
    @hyperc.util.side_effect_decorator
    def __repr__(self):
        return str(self)

def operator_name_to_operator(op):
    expand = {">": "greaterThan", ">=": "greaterThanOrEqual", "<": "lessThan", "<=": "lessThanOrEqual",
              "==": "equal", "!=": "notEqual"}
    for k, v in expand.items():
        if v == op:
            return k
    return None

# H 75-150 is green
def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v


# Define TAKEIF formula
FUNCTIONS = formulas.get_functions()
def STUB_TAKEIF(default, *args):
    return default
FUNCTIONS["TAKEIF"] = STUB_TAKEIF

# Define SELECTFROMRANGE formula
def STUB_SELECTFROMRANGE(*args):
    return 0
FUNCTIONS["SELECTFROMRANGE"] = STUB_SELECTFROMRANGE

# Define WATCH formula
def STUB_WATCH(*args):
    return 0
FUNCTIONS["WATCH"] = STUB_WATCH

class EventNameHolder:
    ename: str
    def __init__(self) -> None:
        self.ename = ""
    def __str__(self):
        v = str(self.ename)
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        return v

class ETable:
    def __init__(self, filename, project_name="my_project") -> None:
        filename = pathlib.PosixPath(filename)
        self.filename = filename
        self.out_filename = ""
        APPENDIX = hyperc.settings.APPENDIX
        hyperc.settings.APPENDIX = hyperc.xtj.str_to_py(str(filename)) + "_" + project_name
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
        self.mod.StaticObject.__annotations__ = {'GOAL': bool}
        self.mod.StaticObject.__annotations__ = {}

        self.mod.StaticObject.__qualname__ = f"{self.session_name}.StaticObject"
        self.mod.HCT_STATIC_OBJECT = self.mod.StaticObject()
        self.mod.HCT_STATIC_OBJECT.GOAL = False
        self.mod.HCT_OBJECTS = {}
        self.methods_classes = {}
        self.methods_classes["StaticObject"] = self.mod.StaticObject
        self.wb_values_only = openpyxl.load_workbook(filename=filename, data_only=True)
        self.metadata = {"plan_steps": [], "plan_exec": []}
        self.plan_log = []

    def get_cellvalue_by_cellname(self, cellname):
        filename, sheet, row, column = hyper_etable.etable_transpiler.split_cell(cellname) 
        py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
        attrname = f"{py_table_name}_{row}"
        return getattr(getattr(self.mod.HCT_STATIC_OBJECT, attrname), column.lower())

    def solver_call(self,goal, extra_instantiations):
        mod=self.mod
        HCT_STATIC_OBJECT = mod.HCT_STATIC_OBJECT
        globals_ = self.methods_classes
        ret = hyperc.solve(goal, globals_=globals_, extra_instantiations=extra_instantiations, work_dir=self.tempdir, 
                            addition_modules=[mod], metadata=self.metadata)
        step_counter = 1
        ename = EventNameHolder()
        for step in self.metadata["plan_exec"]:
            step[0](**step[1])
            for cellvar in step[0].orig_funcobject.effect_vars:  
                filename, sheet, row, column = hyper_etable.etable_transpiler.split_cell(cellvar.cell_str) 
                ftype = step[0].orig_funcobject.formula_type
                log_entry = [step_counter, ftype, ename,
                             f"'{sheet.upper()}'!{column.upper()}", row, self.get_cellvalue_by_cellname(cellvar.cell_str)]
                if ftype == "TAKEIF":
                    ename_l = list(step[0].orig_funcobject.sync_cell)
                    if ename_l:
                        ename_str = ename_l[0]
                        if isinstance(ename_str, hyper_etable.etable_transpiler.StringLikeVariable):
                            ename_str = ename_str.cell_str
                        if not ename_str.endswith('"') and not ename_str.startswith('"') and "!" in ename_str:
                            ename_str = self.get_cellvalue_by_cellname(ename_str)
                        ename.ename = ename_str
                    ename = EventNameHolder()
                self.plan_log.append(log_entry)
            step_counter += 1



    def dump_functions(self, code, filename):
        s_code = ''
        fn = f"{self.tempdir}/{filename}"
        with open(fn, "w+") as f:
            # f.write('from hyperc import not_hasattr')
            f.write('\n')
            for func in code.values():
                f.write(str(func))
                f.write('\n')
                s_code += str(func)
                s_code += '\n'

        f_code = compile(s_code, fn, 'exec')

        exec(f_code, self.mod.__dict__)
        for func_code in code.values():
            self.methods_classes[func_code.name] = self.mod.__dict__[func_code.name]
            self.methods_classes[func_code.name].orig_source = str(func_code)
            self.methods_classes[func_code.name].orig_funcobject = func_code


    def get_new_table(self, table_name, sheet):
        ThisTable = TableElementMeta(table_name, (object,), {'__table_name__': table_name, '__xl_sheet_name__': sheet})
        ThisTable.__annotations__ = {'__table_name__': str, 'recid': int}
        ThisTable.__touched_annotations__ = set()
        ThisTable.__annotations_type_set__ = defaultdict(set)
        self.mod.__dict__[table_name] = ThisTable
        self.classes[table_name] = ThisTable
        self.classes[table_name].__qualname__ = f"{self.session_name}.{table_name}"
        self.mod.HCT_OBJECTS[table_name] = []
        return ThisTable

    def get_object_from_var(self, var):
        py_table_name = hyperc.xtj.str_to_py(f'[{var.filename}]{var.sheet}')
        return self.objects[py_table_name][var.number]

    def calculate(self):

        xl_mdl = formulas.excel.ExcelModel()
        xl_mdl.loads(str(self.filename))
        stl = hyper_etable.spiletrancer.SpileTrancer(self.filename, xl_mdl, self.mod.HCT_STATIC_OBJECT, plan_log=self.plan_log)
        var_mapper = {}
        global_table_type_mapper = {}
        code = {}

        used_cell_set = set()

        for node_key, node_val in xl_mdl.dsp.dmap.nodes.items():
            if ('inputs' in node_val) and ('outputs' in node_val):
                assert len(node_val['outputs']) == 1, f'Currently support only one cell as output'
                output = node_val['outputs'][0]
                out_py = hyperc.xtj.str_to_py(output)
                code_init = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_{out_py}')
                code_init.init.append(f'#{node_key}')
                used_cell_set.add(output)
                for used_cell in itertools.chain(node_val['inputs'].keys(), node_val['outputs']):
                    used_cell_set.add(used_cell)
                for input in node_val['inputs']:
                    filename, sheet, recid, letter = hyper_etable.etable_transpiler.split_cell(input)
                    py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
                    if py_table_name not in self.classes:
                        self.get_new_table(py_table_name, sheet)
                    if isinstance(recid, list):
                        continue
                    sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}")
                    var_name = f'var_tbl_{py_table_name}__hct_direct_ref__{recid}_{letter}'
                    # FIXME: this init code is being used+cleaned in some crazy while-true loop in def clean() in transpiler
                    code_init.init.append(f'{var_name} = HCT_STATIC_OBJECT.{py_table_name}_{recid}.{letter} # TEST HERE')
                    code_init.hasattr_code.append(f'assert HCT_STATIC_OBJECT.{py_table_name}_{recid}.{letter}_not_hasattr == False')

                # formula= hyper_etable.etable_transpiler.EtableTranspiler(
                #     node_key, node_val['inputs'].keys(), output)
                formula = hyper_etable.etable_transpiler.EtableTranspilerEasy(
                    node_key, node_val['inputs'].keys(),
                    output, init_code=code_init, table_type_mapper=global_table_type_mapper, var_mapper=var_mapper)
                formula.transpile_start()
                # set default value for takeif
                var = formula.default
                if isinstance(formula.default, hyper_etable.etable_transpiler.StringLikeConstant):
                    var = formula.default.var
                xl_mdl.cells[output].value = var
                code.update(formula.code)

        # Find what is being watched, and inject watchtakeif sync cells
        watched_takeifs = defaultdict(list)
        for func in code.values():
            if func.watchtakeif:
                watched_takeifs[func.watchtakeif].append(func)
        min_recid = {}
        max_recid = {}
        for watched_takeif_cell, watched_actions in  watched_takeifs.items():
            for w_a in watched_actions:
                cell = list(w_a.effect_vars)[0]
                watch_for = f'{watched_takeif_cell}_{cell.letter}'
                if watch_for not in min_recid:
                    min_recid[watch_for] = cell
                    max_recid[watch_for] = cell
                if cell.number > max_recid[watch_for].number:
                    max_recid[watch_for] = cell
                if cell.number < max_recid[watch_for].number:
                    min_recid[watch_for] = cell

        watch_code = []
        for watch_for, recid in min_recid.items():
            watch_code.append(f"WATCHTAKEIF_{watch_for} = {recid.number}")
        watch_code = "\n".join(watch_code)
        fn=f"{self.tempdir}/hpy_watch_code.py"
        with open(fn, "w+") as f:
            f.write(watch_code)
        f_code=compile(watch_code, fn, 'exec')
        exec(f_code, self.mod.__dict__)

        for func in code.values():
            func.clean()
            for var in func.sync_cell:
                if not isinstance(var, hyper_etable.etable_transpiler.StringLikeVariable):
                    continue
                cell_name = var.get_excel_format()
                if (cell_name in used_cell_set) and (cell_name not in xl_mdl.cells):
                    used_cell_set.remove(cell_name)

        # # look for mergable actions by sync
        deleted_keys = set()
        for func_name_other in list(code.keys()):
            if func_name_other in deleted_keys:
                continue
            for func_name in list(code.keys()):
                #check that funtions is not parent and child
                if func_name_other in deleted_keys:
                    continue
                if code[func_name] is code[func_name_other]:
                    continue
                if (not code[func_name].sync_cell.isdisjoint(code[func_name_other].sync_cell)):
                    code[func_name_other].merge(code[func_name])
                    del code[func_name]
                    deleted_keys.add(func_name)
        
        # merge watchtakeif's
        deleted_keys = set()
        for watchif_func_name in list(code.keys()):
            if watchif_func_name in deleted_keys:
                continue
            if code[watchif_func_name].watchtakeif is None:
                continue
            for watchif_func_name_other in list(code.keys()):
                if code[watchif_func_name_other].watchtakeif is None:
                    continue
                if watchif_func_name_other == watchif_func_name:
                    continue
                if code[watchif_func_name_other].watchtakeif == code[watchif_func_name].watchtakeif:
                    code[watchif_func_name].merge(code[watchif_func_name_other])
                    del code[watchif_func_name_other]
                    deleted_keys.add(watchif_func_name_other)

        deleted_keys = set()
        for watchif_func_name in list(code.keys()):
            deleted = False
            for func_name in list(code.keys()):
                if code[func_name].watchtakeif is not None:
                    continue
                if code[watchif_func_name].watchtakeif is None:
                    continue
                if code[watchif_func_name].watchtakeif in code[func_name].effect_vars:
                    code[func_name].merge(code[watchif_func_name])
                    deleted = True
            if deleted:
                del code[watchif_func_name]

        # update keys
        code = {v.name: v for k, v in code.items()}

        self.dump_functions(code, 'hpy_etable.py')

        # Collect conditional formatting
        # TODO set goal here
        goal_code = defaultdict(list)
        for filename, book in xl_mdl.books.items():
            for worksheet in book[formulas.excel.BOOK].worksheets:
                for rule_cell in worksheet.conditional_formatting._cf_rules:
                    assert len(rule_cell.sqref.ranges) == 1, "only one cell ondition support"
                    sheet = worksheet.title
                    cell = f"'[{filename}]{sheet}'!{rule_cell.sqref.ranges[0].coord}".upper()
                    used_cell_set.add(cell)
                    filename, sheet, recid, letter = hyper_etable.etable_transpiler.split_cell(cell)
                    sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}") + f'_{recid}'
                    for rule in rule_cell.rules:
                        value = hyper_etable.etable_transpiler.formulas_parser(rule.formula[0])[0]
                        if isinstance(value, formulas.tokens.operand.Range):
                            filename_value, sheet_value, recid_value, letter_value = hyper_etable.etable_transpiler.split_cell(
                                rule.formula[0])
                            if filename_value == '':
                                filename_value = filename
                            if sheet_value == '':
                                sheet_value = sheet
                            used_cell_set.add(f"'[{filename_value}]{sheet_value}'!{letter_value.upper()}{recid_value}")
                            sheet_name_value = hyperc.xtj.str_to_py(
                                f"[{filename_value}]{sheet_value}") + f'_{recid_value}'
                            goal_code[cell].append(
                                f'assert HCT_STATIC_OBJECT.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} HCT_STATIC_OBJECT.{sheet_name_value}.{letter_value}')
                        elif isinstance(value, formulas.tokens.operand.Number):
                            goal_code[cell].append(
                                f'assert HCT_STATIC_OBJECT.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} {int(value.attr["name"])}')
                        elif isinstance(value, formulas.tokens.operand.String):
                            goal_code[cell].append(
                                f'assert HCT_STATIC_OBJECT.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} "{value.attr["name"]}"')

        g_c = hyper_etable.etable_transpiler.FunctionCode(name='condition_goal', is_goal=True)
        goal_code_source = {}
        goal_code_source[0] = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_goal_0', is_goal=True)
        goal_code_source[0].output[goal_code_source[0].name].append('HCT_STATIC_OBJECT.GOAL = True')
        goal_code_source[0].output[goal_code_source[0].name].append('pass')

        goal_counter = 0
        for goal_name, g_c in goal_code.items():
            goal_counter_was = goal_counter
            goal_counter = (goal_counter + 1) * len(g_c) - 1
            if goal_counter > goal_counter_was:
                counter_was = 0
                for counter_new in range(goal_counter_was + 1, goal_counter+1):
                    if counter_was == goal_counter_was + 1:
                        counter_was = 0
                    goal_code_source[counter_new] = hyper_etable.etable_transpiler.FunctionCode(
                        name=f'hct_goal_{counter_new}', is_goal=True)
                    goal_code_source[counter_new].operators[goal_code_source[counter_new].name] = copy.copy(goal_code_source[counter_was].operators)
                    goal_code_source[counter_new].output[goal_code_source[counter_new].name].append(
                        'HCT_STATIC_OBJECT.GOAL = True')
                    counter_was += 1

            for idx in goal_code_source:
                goal_code_source[idx].operators[goal_code_source[idx].name].append(f'#{goal_name}')
                goal_code_source[idx].operators[goal_code_source[idx].name].append(g_c[idx % len(g_c)])

        main_goal = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_main_goal', is_goal=True)
        main_goal.operators[main_goal.name].append('assert HCT_STATIC_OBJECT.GOAL == True')
        main_goal.operators[main_goal.name].append('pass')
        goal_code_source['main_goal'] = main_goal
        self.dump_functions(goal_code_source, 'hpy_goals.py')

        code.update(goal_code_source)


        for cell in used_cell_set:

            filename, sheet, recid_ret, letter_ret = hyper_etable.etable_transpiler.split_cell(cell)
            py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
            if isinstance(recid_ret, list):
                recid_ret = range(recid_ret[0], recid_ret[1] + 1)
            else:
                recid_ret = [recid_ret]

            if isinstance(letter_ret, list):
                letter_stop = letter_ret[1]
                letter_next = letter_ret[0]
                letter_ret = [letter_next]
                while letter_next != letter_stop:
                    letter_next = hyperc.util.letter_index_next(letter = letter_next).lower()
                    letter_ret.append(letter_next)
            else:
                letter_ret = [letter_ret]
            for letter in letter_ret:
                for recid in recid_ret:
                    if recid not in self.objects[py_table_name]:
                        if py_table_name not in self.classes:
                            ThisTable = self.get_new_table(py_table_name, sheet)
                        else:
                            ThisTable = self.classes[py_table_name]
                        # if 
                        rec_obj = ThisTable()
                        # rec_obj.__row_record__ = copy.copy(cell)
                        rec_obj.recid = recid
                        rec_obj.__table_name__ += f'[{filename}]{sheet}_{recid}'
                        rec_obj.__touched_annotations__ = set()
                        # ThisTable.__annotations_type_set__ = defaultdict(set)
                        self.objects[py_table_name][recid] = rec_obj
                        self.mod.HCT_OBJECTS[py_table_name].append(rec_obj)
                    self.objects[py_table_name][recid].__touched_annotations__.add(letter)
                    self.objects[py_table_name][recid].__annotations__[(f'{letter}_not_hasattr')] = bool
                    #TODO add type detector
                    # self.classes[py_table_name].__annotations__[letter] = int
                    # rec_obj.__annotations__.add(letter)
                    sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}") + f'_{recid}'
                    if not hasattr(self.mod.HCT_STATIC_OBJECT, sheet_name):
                        setattr(self.mod.HCT_STATIC_OBJECT, sheet_name, self.objects[py_table_name][recid])
                        self.mod.StaticObject.__annotations__[sheet_name] = self.classes[py_table_name]
                    cell = f"'[{filename}]{sheet}'!{letter.upper()}{recid}"
                    if not cell in xl_mdl.cells:
                        raise ReferenceError(f"Referencing empty cell {cell}")
                    if xl_mdl.cells[cell].value is not schedula.EMPTY:
                        cell_value = xl_mdl.cells[cell].value
                        setattr(self.objects[py_table_name][recid], letter, cell_value)
                        setattr(self.objects[py_table_name][recid], f'{letter}_not_hasattr', False)
                        # FIXME: needs type detector, then these lines can be removed -->
                        # self.objects[py_table_name][recid].__class__.__annotations__[letter] = type(cell_value)
                        # self.objects[py_table_name][recid].__annotations__[letter] = type(cell_value)
                        self.objects[py_table_name][recid].__class__.__annotations__[letter] = str  # bug hyperc#453
                        self.objects[py_table_name][recid].__annotations__[letter] = str  # bug hyperc#453 
                        # <-- end FIXME

                    else:
                        # TODO this is stumb for novalue cell. We should use Novalue ????
                        ox_sht, ox_cell_ref = stl.gen_opxl_addr(self.filename, 
                                                        self.objects[py_table_name][recid].__class__.__xl_sheet_name__, 
                                                        letter, recid)
                        xl_orig_calculated_value = self.wb_values_only[ox_sht][ox_cell_ref].value
                        if type(xl_orig_calculated_value) == int or type(xl_orig_calculated_value) == str:
                            setattr(self.objects[py_table_name][recid], letter, xl_orig_calculated_value)
                        else:
                            setattr(self.objects[py_table_name][recid], letter, 0)
                        setattr(self.objects[py_table_name][recid], f'{letter}_not_hasattr', True)
            
        # Type detector
        # Match all group neighbor each other
        # by Breadth-first search now
        # not_double_pass = True
        # while not_double_pass:
        #     not_double_pass = False
        #     for tm in global_table_type_mapper.values():
        #         while tm.visited_group != tm.group:
        #             tm.visited_group = tm.group
        #             tmp_tm_group = copy.copy(tm.group)
        #             for tm_name in tmp_tm_group:
        #                 tm.merge_group(global_table_type_mapper[tm_name])
        #     for tm in global_table_type_mapper.values():
        #         while tm.forward_visited_group != tm.group:
        #             tm.forward_visited_group = tm.group
        #             tmp_tm_group = copy.copy(tm.group)
        #             for tm_name in tmp_tm_group:
        #                 tm.merge_group(global_table_type_mapper[tm_name])
        #         if tm.forward_visited_group != tm.visited_group:
        #             not_double_pass = True

        # for var in var_mapper.values():
        #     if isinstance(var, hyper_etable.etable_transpiler.StringLikeVariable):
        #         if var.is_range:
        #             recid_ret = range(var.number[0], var.number[1]+1)
        #             letter = var.letter[0]
        #         else:
        #             recid_ret = [var.number]
        #             letter = var.letter
        #         py_table_name = hyperc.xtj.str_to_py(f'[{var.filename}]{var.sheet}')
        #         for recid in recid_ret:
        #             line_object = self.objects[py_table_name][recid]
        #             #TODO fix type detector for ranges
        #             # if int in var.types:
        #                 # line_object.__annotations__[letter] = int
        #                 # line_object.__class__.__annotations__[letter] = int
        #             line_object.__annotations__[letter] = int
        #             line_object.__class__.__annotations__[letter] = int

        # stack_code = ''
        # for cell in used_cell_set:
        #     filename, sheet, recid_ret, letter = hyper_etable.etable_transpiler.split_cell(cell)
        #     stack_code = stack_code_gen(hyperc.xtj.str_to_py(f'[{filename}]{sheet}'))
        #     break

        stack_code = stack_code_gen_all(self.objects)

        fn = f"{self.tempdir}/hpy_stack_code.py"
        with open(fn, "w+") as f:
            f.write(str(stack_code))

        f_code = compile(stack_code, fn, 'exec')
        exec(f_code, self.mod.__dict__)

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
                # init_f_code.append(
                    # f'self.{par_name}_not_hasattr = True')  # TODO: statically set to true instead of asking in parameters
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
        HCT_STATIC_OBJECT = self.mod.HCT_STATIC_OBJECT
        init_f_code = []
        init_f_code.append(f"self.GOAL = False")
        for attr_name, attr_type in self.mod.StaticObject.__annotations__.items():
            init_f_code.append(f"self.{attr_name} = HCT_STATIC_OBJECT.{attr_name}")  # if it does not ignore, fix it!
        if init_f_code:

            full_f_code = '\n    '.join(init_f_code)
            full_code = f"def hct_stf_init(self):\n    {full_f_code}"
            fn = f"{self.tempdir}/hpy_stf_init_{self.mod.StaticObject.__name__}.py"
            open(fn, "w+").write(full_code)
            f_code = compile(full_code, fn, 'exec')
            exec(f_code, self.mod.__dict__)
            self.mod.StaticObject.__init__ = self.mod.__dict__["hct_stf_init"]
            self.mod.StaticObject.__init__.__name__ = "__init__"


        self.methods_classes.update(self.classes)
        just_classes = list(filter(lambda x: isinstance(x, type), self.methods_classes.values()))

        # plan_or_invariants = hyperc.solve(self.methods_classes[main_goal.name], self.methods_classes, just_classes, HCT_STATIC_OBJECT)

        plan_or_invariants = self.solver_call(goal=self.methods_classes[main_goal.name],
                                              extra_instantiations=just_classes)
        print("finish")

        stl.calculate_excel()
        dirn = os.path.dirname(self.filename)
        new_dirname = os.path.join(dirn, f"{self.filename.name}_out")
        try:
            mkdir(new_dirname)
        except FileExistsError:
            pass
        new_dirname_forfile = os.path.join(dirn, f"{self.filename.name}_out", str(int(time.time())))
        mkdir(new_dirname_forfile)
        stl.write(new_dirname_forfile)

        self.out_filename = os.path.join(new_dirname_forfile, self.filename.name)
        return self.out_filename

        # # xl_mdl.dsp.dispatch()
        # print('Finished excel-model')


        # xl_mdl.calculate({"'[EXTRA.XLSX]EXTRA'!A1:B1": [[1, 1]]})

        # books = _res2books(xl_mdl.write(xl_mdl.books))

        # msg = '%sCompared overwritten results in %.2fs.\n' \
        #         '%sComparing fresh written results.'

        # res_book = _res2books(xl_mdl.write())
