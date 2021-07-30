from collections import defaultdict
from os import mkdir
import string
import glob
import formulas.excel
import formulas
import hyperc
import hyperc.util
import hyperc.settings
import hyper_etable.etable_transpiler
import hyper_etable.spiletrancer
import hyper_etable.cell_resolver
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
import hyper_etable.util
import hyper_etable.pysourcebuilder

hyperc.settings.IGNORE_MISSING_ATTR_BRANCH = 1


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
                l_all_hasattr_drop.append(f"DATA.{cname}_{idx}.{col}_not_hasattr = True")

    drop_content = "\n    ".join(l_all_hasattr_drop)
    warrants = '\n    '.join(hyper_etable.etable_transpiler.generate_ne_warrants(drop_content))
    scode = f"""def _stack_drop():
    pass
    {warrants}
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
def STUB_WATCHTAKEIF(*args):
    return 0
FUNCTIONS["WATCHTAKEIF"] = STUB_WATCHTAKEIF

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
    def __init__(self, filenames, project_name="my_project") -> None:
        if isinstance(filenames,list):
            filenames = [pathlib.PosixPath(f) for f in filenames]
            self.filename = filenames[0] #TODO currently only one file support
        else:
            self.filename = pathlib.PosixPath(filenames)
        if 'xlsx' == os.path.splitext(self.filename)[1][1:].lower():
            self.enable_precalculation = False
        else:
            self.enable_precalculation = True
        self.STATIC_STORAGE_NAME = 'DATA'

        self.out_filename = ""
        APPENDIX = hyperc.settings.APPENDIX
        hyperc.settings.APPENDIX = hyperc.xtj.str_to_py(str(self.filename)) + "_" + project_name
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
        self.methods_classes = {}

        self.mod.DefinedTables = type("DefinedTables", (object, ), {})
        self.mod.DefinedTables.__annotations__ = {}
        self.mod.DefinedTables.__qualname__ = f"{self.session_name}.DefinedTables"
        self.mod.DEFINED_TABLES = self.mod.DefinedTables()
        self.methods_classes["DefinedTables"] = self.mod.DefinedTables

        self.mod.StaticObject = type("StaticObject", (object, ), {})
        self.mod.StaticObject.__annotations__ = {}
        self.mod.StaticObject.__qualname__ = f"{self.session_name}.StaticObject"
        self.mod.DATA = self.mod.StaticObject()
        self.mod.DATA.GOAL = False
        self.mod.HCT_OBJECTS = {}
        self.methods_classes["StaticObject"] = self.mod.StaticObject

        self.wb_values_only = openpyxl.load_workbook(filename=self.filename, data_only=True)
        self.wb_with_formulas = openpyxl.load_workbook(filename=self.filename)
        self.metadata = {"plan_steps": [], "plan_exec": []}
        self.plan_log = []
        self.cells_value = {}
        self.range_resolver = hyper_etable.cell_resolver.RangeResolver(os.path.basename(self.filename), self.wb_with_formulas)
        self.plan_or_invariants = None
        self.source_code = defaultdict(list)

    def get_cellvalue_by_cellname(self, cellname):
        filename, sheet, row, column = hyper_etable.etable_transpiler.split_cell(cellname) 
        py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
        attrname = f"{py_table_name}_{row}"
        return getattr(getattr(self.mod.DATA, attrname), column.upper())

    def get_row_by_cellname(self, cellname):
        filename, sheet, row, column = hyper_etable.etable_transpiler.split_cell(cellname) 
        py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
        attrname = f"{py_table_name}_{row}"
        return getattr(self.mod.DATA, attrname)

    def solver_call_simple(self,goal, extra_instantiations):
        return hyperc.solve(goal, globals_=self.methods_classes, extra_instantiations=extra_instantiations, work_dir=self.tempdir, 
                            addition_modules=[self.mod])

    def solver_call_simple_wo_exec(self):
        def gg(s, g, e):
            hyperc.solve(g, globals_=s.methods_classes, extra_instantiations=e, work_dir=s.tempdir, 
                            addition_modules=[s.mod], metadata=s.metadata)
        gg(self,self.methods_classes[self.main_goal.name],
                                              list(filter(lambda x: isinstance(x, type), self.methods_classes.values())))
                        
        

    def solver_call(self,goal, extra_instantiations):
        mod=self.mod
        DATA = mod.DATA
        globals_ = self.methods_classes
        ret = hyperc.solve(goal, globals_=globals_, extra_instantiations=extra_instantiations, work_dir=self.tempdir, 
                            addition_modules=[mod], metadata=self.metadata)
        step_counter = 1
        sheetmap = {s.upper():s for s in self.wb_values_only.sheetnames}
        ename = EventNameHolder()
        for step in self.metadata["plan_exec"]:
            substep_counter = 0
            orig_vars = {}
            for cellvar in step[0].orig_funcobject.effect_vars:
                if cellvar.is_range:
                    recid_ret = range(cellvar.number[0], cellvar.number[1]+1)
                    letter = cellvar.letter[0]
                else:
                    recid_ret = [cellvar.number]
                    letter = cellvar.letter
                for number in recid_ret:
                    cell = hyper_etable.cell_resolver.PlainCell(
                        filename=cellvar.cell.filename, sheet=cellvar.cell.sheet, letter=letter, number=number)
                    orig_vars[str(cell)] = self.get_cellvalue_by_cellname(str(cell))
            step[0](**step[1])
            for cellvar in step[0].orig_funcobject.effect_vars:
                if cellvar.is_range:
                    recid_ret = range(cellvar.number[0], cellvar.number[1]+1)
                    letter = cellvar.letter[0]
                else:
                    recid_ret = [cellvar.number]
                    letter = cellvar.letter
                for number in recid_ret:
                    cell = hyper_etable.cell_resolver.PlainCell(
                        filename=cellvar.cell.filename, sheet=cellvar.cell.sheet, letter=letter, number=number)
                    new_value = self.get_cellvalue_by_cellname(str(cell))
                    ftype = step[0].orig_funcobject.formula_type
                    if ftype == "TAKEIF":
                        explain_type = "Decide whether to update value"
                    elif ftype == "SELECTFROMRANGE":
                        explain_type = "Choose one value from a list"
                    else:
                        explain_type = "(formula recalculation)"

                    if new_value == orig_vars[str(cell)] and ftype == "TAKEIF":
                        continue
                    filename, sheet, row, column = hyper_etable.etable_transpiler.split_cell(str(cell))
                    leftmost = ""
                    for ltr in string.ascii_uppercase:
                        colval = self.wb_values_only[sheetmap[sheet]][f"{ltr}{row}"].value
                        if type(colval) == str and len(colval) > 0:
                            leftmost = colval
                            break
                    topmost = ""
                    i = 0
                    prev_empty = False
                    for r in self.wb_values_only[sheetmap[sheet]].rows:
                        colval = r[string.ascii_uppercase.index(column.upper())].value
                        if type(colval) == str and len(colval) > 0:
                            if prev_empty == True:
                                topmost = colval
                            prev_empty = False
                        elif colval == None or colval == "":
                            prev_empty = True
                        else:
                            prev_empty = False
                        i += 1
                        if i >= row: break
                    log_entry = [step_counter, explain_type, ename, leftmost, topmost,
                                f"'{sheet.upper()}'!{column.upper()}", row, orig_vars[str(cell)],
                                new_value,
                                "'"+",".join(step[0].orig_funcobject.formula_str).replace(f"[{filename.upper()}]", "")]
                    if ftype == "TAKEIF":
                        #TODO load string from openpyxl
                        # ename_l = list(step[0].orig_funcobject.sync_cell)
                        # if ename_l:
                        #     ename_str = ename_l[0]
                        #     if isinstance(ename_str, hyper_etable.etable_transpiler.StringLikeVariable):
                        #         ename_str = ename_str.cell_str
                        #     ename_str = str(ename_str)
                        #     if not ename_str.endswith('"') and not ename_str.startswith('"') and "!" in ename_str:
                        #         ename_str = self.get_cellvalue_by_cellname(ename_str)
                        #     ename.ename = ename_str
                        ename = EventNameHolder()
                    self.plan_log.append(log_entry)
                    substep_counter += 1
            step_counter += 1



    def dump_functions(self, code, filename):
        s_code = ''
        fn = f"{self.tempdir}/{filename}"
        with open(fn, "w+") as f:
            for func in code.values():
                s_code += str(func)
            f.write(s_code)
        f_code = compile(s_code, fn, 'exec')

        exec(f_code, self.mod.__dict__)
        for func_code in code.values():
            self.methods_classes[func_code.name] = self.mod.__dict__[func_code.name]
            self.methods_classes[func_code.name].orig_source = str(func_code)
            self.methods_classes[func_code.name].orig_funcobject = func_code


    def get_new_table(self, table_name, sheet):
        ThisTable = TableElementMeta(f'{table_name}_Class', (object,), {'__table_name__': table_name, '__xl_sheet_name__': sheet})
        ThisTable.__annotations__ = {'__table_name__': str}
        ThisTable.__touched_annotations__ = set()
        ThisTable.__annotations_type_set__ = defaultdict(set)
        self.mod.__dict__[f'{table_name}_Class'] = ThisTable
        self.classes[table_name] = ThisTable
        self.classes[table_name].__qualname__ = f"{self.session_name}.{table_name}_Class"
        self.mod.HCT_OBJECTS[table_name] = []
        return ThisTable

    def get_object_from_var(self, var):
        py_table_name = hyperc.xtj.str_to_py(f'[{var.filename}]{var.sheet}')
        return self.objects[py_table_name][var.number]

    def open_dump(self, has_header=False, addition_python_files=[]):
        xl_mdl = formulas.excel.ExcelModel()
        xl_mdl.loads(str(self.filename))
        self.stl = hyper_etable.spiletrancer.SpileTrancer(self.filename, xl_mdl, self.mod.DATA, plan_log=self.plan_log)
        filename_case_remap_workaround = {}

        goal_code_source = {}

        self.main_goal = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_main_goal', is_goal=True)
        self.main_goal.operators[self.main_goal.name].append('assert DATA.GOAL == True')
        self.main_goal.operators[self.main_goal.name].append('pass')
        goal_code_source['main_goal'] = self.main_goal

        # Load used cell
        for wb_sheet in self.wb_values_only:
            sheet = wb_sheet.title
            filename = self.filename
            filename = filename_case_remap_workaround.get(filename, filename)
            # py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
            py_table_name = hyperc.xtj.str_to_py(f'{sheet}') # warning only sheet in 
            header_map = {}
            header_back_map = {}
            if has_header:
                is_header = True
            else:
                is_header = False
            for row in wb_sheet.iter_rows():
                if py_table_name not in self.classes:
                    ThisTable = self.get_new_table(py_table_name, sheet)
                else:
                    ThisTable = self.classes[py_table_name]
                recid = list(row)[0].row
                rec_obj = ThisTable()
                if has_header:
                    rec_obj.__header_back_map__ = header_back_map
                rec_obj.__recid__ = recid
                rec_obj.__table_name__ += f'[{filename}]{sheet}_{recid}'
                rec_obj.__touched_annotations__ = set()
                self.objects[py_table_name][recid] = rec_obj
                self.mod.HCT_OBJECTS[py_table_name].append(rec_obj)
                sheet_name = hyperc.xtj.str_to_py(f"{sheet}") + f'_{recid}'
                if not hasattr(self.mod.DATA, sheet_name):
                    setattr(self.mod.DATA, sheet_name, self.objects[py_table_name][recid])
                    self.mod.StaticObject.__annotations__[sheet_name] = self.classes[py_table_name]
                
                rec_obj.__py_sheet_name__ = sheet_name

                for _cell in row:
                    xl_orig_calculated_value = getattr(_cell, "value", None)
                    if xl_orig_calculated_value is None:
                        continue
                    letter = _cell.column_letter
                    if is_header:
                        # if xl_orig_calculated_value is None:
                        #     continue
                        header_map[letter] = hyperc.xtj.str_to_py(xl_orig_calculated_value)
                        header_back_map[hyperc.xtj.str_to_py(xl_orig_calculated_value)] = letter
                        continue
                    cell = hyper_etable.cell_resolver.PlainCell(filename=filename, sheet=sheet, letter=letter, number=recid)
                    if has_header:
                        column_name = header_map.get(letter, None)
                        #Skip column with empty header bug #176
                        if column_name is None or column_name == "":
                            continue
                    else:
                        column_name = letter
                    if has_header:
                        self.objects[py_table_name][recid].__header_back_map__ = header_back_map
                    # Declare and load defined table names
                    defined_table_name = self.range_resolver.get_table_by_cell(cell)
                    if defined_table_name is not None:
                        for dtn_raw in defined_table_name:
                            dtn = hyperc.xtj.str_to_py(dtn_raw)
                            if dtn not in self.mod.DefinedTables.__annotations__:
                                self.mod.DefinedTables.__annotations__[dtn] = set
                                setattr(self.mod.DEFINED_TABLES, dtn, set())
                            getattr(self.mod.DEFINED_TABLES, dtn).add(self.objects[py_table_name][recid])

                    self.objects[py_table_name][recid].__touched_annotations__.add(column_name)

                    if xl_orig_calculated_value in ['#NAME?', '#VALUE!']:
                        raise Exception(f"We don't support table with error cell {cell}")
                    if (type(xl_orig_calculated_value) == bool or type(xl_orig_calculated_value) == int or type(xl_orig_calculated_value) == str):
                        setattr(self.objects[py_table_name][recid], column_name, xl_orig_calculated_value)
                        self.objects[py_table_name][recid].__class__.__annotations__[column_name] = str
                        self.objects[py_table_name][recid].__touched_annotations__.add(column_name) 
                    else:
                        setattr(self.objects[py_table_name][recid], column_name, '')
                        self.objects[py_table_name][recid].__class__.__annotations__[column_name] = str
                        self.objects[py_table_name][recid].__touched_annotations__.add(column_name)
                if is_header:
                    is_header = False
                    continue

                for column_name in header_back_map.keys():
                    if not hasattr(rec_obj, column_name):
                        setattr(self.objects[py_table_name][recid], column_name, '')
                        self.objects[py_table_name][recid].__class__.__annotations__[column_name] = str
                        self.objects[py_table_name][recid].__touched_annotations__.add(column_name)

                    

        # Dump defined table names
        init_f_code = []
        for attr_name, attr_type in self.mod.DefinedTables.__annotations__.items():
            init_f_code.append(f"self.{attr_name} = DEFINED_TABLES.{attr_name}")  # if it does not ignore, fix it!
        self.mod.DefinedTables.__annotations__['GOAL'] = bool
        if init_f_code:
            full_f_code = '\n    '.join(init_f_code)
            full_code = f"def hct_dt_init(self):\n    {full_f_code}"
            fn = f"{self.tempdir}/hpy_dt_init.py"
            open(fn, "w+").write(full_code)
            f_code = compile(full_code, fn, 'exec')
            exec(f_code, self.mod.__dict__)
            self.mod.DefinedTables.__init__ = self.mod.__dict__["hct_dt_init"]
            self.mod.DefinedTables.__init__.__name__ = "__init__"


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
        self.mod.DATA.GOAL = False
        self.mod.StaticObject.__annotations__['GOAL'] = bool
        init_f_code = []
        for attr_name, attr_type in self.mod.StaticObject.__annotations__.items():
            init_f_code.append(f"self.{attr_name} = DATA.{attr_name}")  # if it does not ignore, fix it!
        self.mod.StaticObject.__annotations__['GOAL'] = bool
        if init_f_code:

            full_f_code = '\n    '.join(init_f_code)
            full_code = f"def hct_stf_init(self):\n    {full_f_code}"
            fn = f"{self.tempdir}/hpy_stf_init_{self.mod.StaticObject.__name__}.py"
            open(fn, "w+").write(full_code)
            f_code = compile(full_code, fn, 'exec')
            exec(f_code, self.mod.__dict__)
            self.mod.StaticObject.__init__ = self.mod.__dict__["hct_stf_init"]
            self.mod.StaticObject.__init__.__name__ = "__init__"

        # dump goals and actions
        self.dump_functions(goal_code_source, 'hpy_goals.py')

        # addition python code
        for code_file in addition_python_files:
            addition_code = open(code_file, "r").read()
            if addition_code.startswith("from"):  # workaround for module imports
                addition_code = "#"+addition_code
            f_code = compile(addition_code, code_file, 'exec')
            exec(f_code, self.mod.__dict__)
            for f_name in f_code.co_names:
                if "." in f_name: continue  # workaround for module names
                self.methods_classes[f_name] = self.mod.__dict__[f_name]
        # for f in self.mod.__dict__:
        #     if isinstance(self.mod.__dict__[f], types.FunctionType):
        #         self.methods_classes[f] = self.mod.__dict__[f]

        self.methods_classes.update(self.classes)
        # dump classes as python code
        for c in itertools.chain([TableElementMeta], self.classes.values(), [self.mod.StaticObject, self.mod.DefinedTables]):
            self.source_code['classes'].append(hyper_etable.pysourcebuilder.build_source_from_class(c, ['__table_name__','__xl_sheet_name__']).end())

        # dump object as python code
        self.source_code['classes'].append('DATA = StaticObject()')


    def dump_py(self, dir=None):
        """"Dump classes as python code"""
        if dir is None:
            dir =  self.filename.parent
        try:
            os.mkdir(dir)
        except FileExistsError:
            pass 
        for f_name, code  in self.source_code.items():
            code_file = os.path.join(dir, f'{f_name}.py')
            s_code =""
            for func in code:
                s_code += str(func)
                s_code += '\n'
            open(code_file, "w+").write(s_code)

    # def solver_call_call_simple(self):

    #     plan_or_invariants = self.solver_call_simple(goal=self.methods_classes[self.main_goal.name],
    #                                           extra_instantiations=list(filter(lambda x: isinstance(x, type), self.methods_classes.values())))
    #     print("finish")     
    def solve_dump(self, has_header=False):
        self.open_dump(has_header)
        ret = self.solver_call_simple(goal=self.methods_classes[self.main_goal.name],
                                              extra_instantiations=list(filter(lambda x: isinstance(x, type), self.methods_classes.values())))
        self.plan_or_invariants = ret

    def save_plan(self, prefix="DATA.", exec_plan=False, out_dir=None):
        """Dump plan as python code"""
        if out_dir is None:
            out_dir =  os.path.join(self.filename.parent, 'out')
        code_file = pathlib.Path(os.path.join(out_dir,f'{os.path.splitext(self.filename.name)[0]}.py'))
        try:
            os.mkdir(out_dir)
        except FileExistsError:
            pass 
        code = []
        for step in self.metadata["plan_exec"]:
            args = ", ".join([f'{k}={prefix}{a.__py_sheet_name__}' for k, a in step[1].items()])
            code.append(f'{step[0].__name__}({args})')
        code_str = "\n".join(code)
        with open(code_file, "w+") as f:
            f.write(code_str)
        if exec_plan:
            f_code = compile(code_str, code_file, 'exec')
            exec(f_code, self.mod.__dict__)

    def run_plan(self, py_plan_filename):
        plan_code_str = open(py_plan_filename, "r").read()
        f_code = compile(plan_code_str, py_plan_filename, 'exec')
        exec(f_code, self.mod.__dict__)

    def save_dump(self, has_header=False, out_dir=None):
        if out_dir is None:
            out_dir =  os.path.join(self.filename.parent, 'out')
        try:
            os.mkdir(out_dir)
        except FileExistsError:
            pass 
        for table in self.mod.HCT_OBJECTS.values():
            for row in table:
                sheet_name = row.__xl_sheet_name__
                recid = row.__recid__
                for attr_name in row.__touched_annotations__:
                    if has_header:
                        letter = row.__header_back_map__[attr_name]
                    else:
                        letter = attr_name
                    self.wb_values_only[sheet_name][f'{letter}{recid}'] = getattr(row, attr_name)
        
        outfile_path = os.path.join(out_dir, f'{self.filename.name}')
        self.wb_values_only.save(outfile_path)
        return outfile_path

    def calculate(self):

        # g=self.get_range_name_by_cell("'[fff]ggg'!B1")
        # gg = hyper_etable.etable_transpiler.split_cell(
        #     "ONESTABLE[PLUS ONES]")
        xl_mdl = formulas.excel.ExcelModel()
        xl_mdl.loads(str(self.filename))
        # 
        self.stl = hyper_etable.spiletrancer.SpileTrancer(self.filename, xl_mdl, self.mod.DATA, plan_log=self.plan_log)
        var_mapper = {}
        global_table_type_mapper = {}
        code = {}
        filename_case_remap_workaround = {}

        used_cell_set = set()

        for ws in self.wb_with_formulas.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value is None:
                        continue # skip empty cell
                    text_formula = str(cell.value)
                    current_cell = hyper_etable.cell_resolver.PlainCell(
                        filename=self.filename, sheet=ws.title, letter=cell.column_letter, number=cell.row)
                    if not text_formula.startswith("="):
                        self.cells_value[current_cell] = cell.value
                        continue # pass only formulas
                    output = hyper_etable.etable_transpiler.StringLikeVariable(
                        var_map=var_mapper, filename=self.filename, sheet=ws.title, letter=cell.column_letter, number=cell.row)
                    out_py = hyperc.xtj.str_to_py(f'[{output.filename}]{output.sheet}!{output.letter}{output.number}')
                    code_init = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_{out_py}')
                    code_init.init.append(f'#{text_formula}')

                    used_cell_set.add(current_cell)
                    formula = hyper_etable.etable_transpiler.EtableTranspiler(
                        formula=text_formula, range_resolver= self.range_resolver,
                        output=output, init_code=code_init, table_type_mapper=global_table_type_mapper, var_mapper=var_mapper)
                    formula.transpile_start()
                    # set default value for takeif
                    var = formula.default
                    if isinstance(formula.default, hyper_etable.etable_transpiler.StringLikeConstant):
                        var = formula.default.var
                    self.cells_value[current_cell] = var
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
            watch_code.append(f"WATCHTAKEIF_MAX_{watch_for} = {max_recid[watch_for].number+1}")
        if len(watch_code) > 0:
            watch_code = "\n".join(watch_code)
            fn=f"{self.tempdir}/hpy_watch_code.py"
            with open(fn, "w+") as f:
                f.write(watch_code)
            f_code=compile(watch_code, fn, 'exec')
            exec(f_code, self.mod.__dict__)

        for func in code.values():
            used_cell_set.update(set([i.cell for i in func.input_variables]))
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


        # Collect conditional formatting
        # TODO set goal here
        goal_code = defaultdict(list)
        goal_code_used_vars = set()
        for filename, book in xl_mdl.books.items():
            filename = filename_case_remap_workaround.get(filename, filename)
            for worksheet in book[formulas.excel.BOOK].worksheets:
                for rule_cell in worksheet.conditional_formatting._cf_rules:
                    assert len(rule_cell.sqref.ranges) == 1, "Only one cell conditional rule is supported"
                    sheet = worksheet.title
                    assert rule_cell.sqref.ranges[0].size == {'columns': 1, 'rows': 1}, "Ranged rules are not supported"
                    cell = f"'[{filename}]{sheet}'!{rule_cell.sqref.ranges[0].coord}"
                    col_letter = hyper_etable.util.get_char_from_index(rule_cell.sqref.ranges[0].bounds[0]-1)
                    row = rule_cell.sqref.ranges[0].bounds[1]
                    current_cell = hyper_etable.cell_resolver.PlainCell(
                        filename=filename, sheet=sheet, letter=col_letter, number=row)
                    used_cell_set.add(current_cell)
                    goal_code_used_vars.add(current_cell)
                    filename_, sheet, recid, letter = hyper_etable.etable_transpiler.split_cell(cell)
                    sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}") + f'_{recid}'
                    for rule in rule_cell.rules:
                        value = hyper_etable.etable_transpiler.formulas_parser(rule.formula[0])[0]
                        if isinstance(value, formulas.tokens.operand.Range):
                            filename_value, sheet_value, recid_value, letter_value = hyper_etable.etable_transpiler.split_cell(
                                rule.formula[0])
                            # if filename_value == '':
                            filename_value = filename
                            if sheet_value == '':
                                sheet_value = sheet
                            # used_cell_set.add(f"'[{filename_value}]{sheet_value}'!{letter_value.upper()}{recid_value}")
                            current_cell = hyper_etable.cell_resolver.PlainCell(
                                filename=filename_value, sheet=sheet_value, letter=letter_value.upper(), number=recid_value)
                            goal_code_used_vars.add(current_cell)
                            used_cell_set.add(current_cell)
                            sheet_name_value = hyperc.xtj.str_to_py(
                                f"[{filename_value}]{sheet_value}") + f'_{recid_value}'
                            goal_code[cell].append([
                                f'assert DATA.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} DATA.{sheet_name_value}.{letter_value}',
                                f'assert DATA.{sheet_name}.{letter}_not_hasattr == False', 
                                f'assert DATA.{sheet_name_value}.{letter_value}_not_hasattr == False'])
                        elif isinstance(value, formulas.tokens.operand.Number):
                            if str(value.attr["name"]) == "TRUE":
                                goal_code[cell].append([
                                    f'assert DATA.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} True',
                                    f'assert DATA.{sheet_name}.{letter}_not_hasattr == False'])
                            elif str(value.attr["name"]) == "FALSE":
                                goal_code[cell].append([
                                    f'assert DATA.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} False',
                                    f'assert DATA.{sheet_name}.{letter}_not_hasattr == False'])
                            else:
                                goal_code[cell].append([
                                    f'assert DATA.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} {int(value.attr["name"])}',
                                    f'assert DATA.{sheet_name}.{letter}_not_hasattr == False'])
                        elif isinstance(value, formulas.tokens.operand.String):
                            goal_code[cell].append([
                                f'assert DATA.{sheet_name}.{letter} {operator_name_to_operator(rule.operator)} "{value.attr["name"]}"',
                                f'assert DATA.{sheet_name}.{letter}_not_hasattr == False'])

        g_c = hyper_etable.etable_transpiler.FunctionCode(name='condition_goal', is_goal=True)
        goal_code_source = {}
        goal_code_source[0] = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_goal_0', is_goal=True)
        goal_code_source[0].output[goal_code_source[0].name].append('DATA.GOAL = True')
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
                        'DATA.GOAL = True')
                    goal_code_source[counter_new].input_variables.update(goal_code_used_vars)
                    goal_code_source[counter_new].all_variables.update(goal_code_used_vars)
                    counter_was += 1

            for idx in goal_code_source:
                goal_code_source[idx].operators[goal_code_source[idx].name].append(f'#{goal_name}')
                goal_code_source[idx].operators[goal_code_source[idx].name].extend(g_c[idx % len(g_c)])


        main_goal = hyper_etable.etable_transpiler.FunctionCode(name=f'hct_main_goal', is_goal=True)
        main_goal.operators[main_goal.name].append('assert DATA.GOAL == True')
        main_goal.operators[main_goal.name].append('pass')
        goal_code_source['main_goal'] = main_goal

        # delete tailing actions
        unused_cell_set = set()
        some_found = True
        while some_found: #double pass search
            some_found = False
            for function_key_deletable in list(code.keys()):
                func_deletable = code.get(function_key_deletable, None)
                if func_deletable is None:
                    continue
                found = False
                effect_vars = hyper_etable.etable_transpiler.unpack_cell(func_deletable.effect_vars)
                # look in actions
                for function_key in list(code.keys()):
                    func = code.get(function_key, None)
                    if func is None:
                        continue
                    input_variables = hyper_etable.etable_transpiler.unpack_cell(func.input_variables)
                    if effect_vars & input_variables:
                        found = True
                        break
                if found:
                    continue
                # look in goals
                if effect_vars & goal_code_used_vars:
                    found = True
                    continue
                if not found:
                    unused_cell_set.update(effect_vars)
                    del code[function_key_deletable]
                    some_found = True
        # Generate init code
        [c.gen_init() for c in code.values()]

        # Load used cell
        for cell in used_cell_set:
            filename = cell.filename
            sheet = cell.sheet
            recid_ret = cell.number

            letter_ret = cell.letter

            filename = filename_case_remap_workaround.get(filename, filename)
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
                    letter_next = hyperc.util.letter_index_next(letter = letter_next).upper()
                    letter_ret.append(letter_next)
            else:
                letter_ret = [letter_ret]
            for letter in letter_ret:
                for recid in recid_ret:
                    cell = hyper_etable.cell_resolver.PlainCell(filename=filename, sheet=sheet, letter=letter, number=recid)
                    if cell in unused_cell_set:
                        continue
                    if recid not in self.objects[py_table_name]:
                        if py_table_name not in self.classes:
                            ThisTable = self.get_new_table(py_table_name, sheet)
                        else:
                            ThisTable = self.classes[py_table_name]
                        # if 
                        rec_obj = ThisTable()
                        # rec_obj.__row_record__ = copy.copy(cell)
                        rec_obj.__table_name__ += f'[{filename}]{sheet}_{recid}'
                        rec_obj.__touched_annotations__ = set()
                        # ThisTable.__annotations_type_set__ = defaultdict(set)
                        self.objects[py_table_name][recid] = rec_obj
                        self.mod.HCT_OBJECTS[py_table_name].append(rec_obj)
                    
                    # Declare and load defined table names
                    defined_table_name = self.range_resolver.get_table_by_cell(cell)
                    if defined_table_name is not None:
                        for dtn_raw in defined_table_name:
                            dtn = hyperc.xtj.str_to_py(dtn_raw)
                            if dtn not in self.mod.DefinedTables.__annotations__:
                                self.mod.DefinedTables.__annotations__[dtn] = set
                                setattr(self.mod.DEFINED_TABLES, dtn, set())
                            getattr(self.mod.DEFINED_TABLES, dtn).add(self.objects[py_table_name][recid])

                    self.objects[py_table_name][recid].__touched_annotations__.add(letter)
                    self.objects[py_table_name][recid].__annotations__[(f'{letter}_not_hasattr')] = bool
                    #TODO add type detector
                    # self.classes[py_table_name].__annotations__[letter] = int
                    # rec_obj.__annotations__.add(letter)
                    sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}") + f'_{recid}'
                    if not hasattr(self.mod.DATA, sheet_name):
                        setattr(self.mod.DATA, sheet_name, self.objects[py_table_name][recid])
                        self.mod.StaticObject.__annotations__[sheet_name] = self.classes[py_table_name]
                    # assert cell in self.cells_value, f"Lost value for cell {cell}"
                    if cell not in self.cells_value or self.cells_value[cell] is None:
                        # TODO this is stumb for novalue cell. We should use Novalue ????
                        ox_sht, ox_cell_ref = self.stl.gen_opxl_addr(self.filename, 
                                                        self.objects[py_table_name][recid].__class__.__xl_sheet_name__, 
                                                        letter, recid)
                        xl_orig_calculated_value = self.wb_values_only[ox_sht][ox_cell_ref].value
                        if xl_orig_calculated_value in ['#NAME?', '#VALUE!']  and self.enable_precalculation:
                            raise Exception("We don't support table with error cell")
                        elif not self.enable_precalculation:
                            xl_orig_calculated_value = ''
                        if (type(xl_orig_calculated_value) == bool or type(xl_orig_calculated_value) == int or type(xl_orig_calculated_value) == str) and self.enable_precalculation:
                            setattr(self.objects[py_table_name][recid], letter, xl_orig_calculated_value)
                            self.objects[py_table_name][recid].__class__.__annotations__[letter] = str
                        else:
                            setattr(self.objects[py_table_name][recid], letter, '')
                            self.objects[py_table_name][recid].__class__.__annotations__[letter] = str
                        setattr(self.objects[py_table_name][recid], f'{letter}_not_hasattr', True)

                    else:
                        setattr(self.objects[py_table_name][recid], letter, self.cells_value[cell])
                        setattr(self.objects[py_table_name][recid], f'{letter}_not_hasattr', False)
                        # FIXME: needs type detector, then these lines can be removed -->
                        # self.objects[py_table_name][recid].__class__.__annotations__[letter] = type(cell_value)
                        # self.objects[py_table_name][recid].__annotations__[letter] = type(cell_value)
                        self.objects[py_table_name][recid].__class__.__annotations__[letter] = str  # bug hyperc#453
                        self.objects[py_table_name][recid].__annotations__[letter] = str  # bug hyperc#453 
                        # <-- end FIXME
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

        # Dump defined table names
        init_f_code = []
        for attr_name, attr_type in self.mod.DefinedTables.__annotations__.items():
            init_f_code.append(f"self.{attr_name} = DEFINED_TABLES.{attr_name}")  # if it does not ignore, fix it!
        self.mod.DefinedTables.__annotations__['GOAL'] = bool
        if init_f_code:
            full_f_code = '\n    '.join(init_f_code)
            full_code = f"def hct_dt_init(self):\n    {full_f_code}"
            fn = f"{self.tempdir}/hpy_dt_init.py"
            open(fn, "w+").write(full_code)
            f_code = compile(full_code, fn, 'exec')
            exec(f_code, self.mod.__dict__)
            self.mod.DefinedTables.__init__ = self.mod.__dict__["hct_dt_init"]
            self.mod.DefinedTables.__init__.__name__ = "__init__"


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
        self.mod.DATA.GOAL = False
        self.mod.StaticObject.__annotations__['GOAL'] = bool
        init_f_code = []
        for attr_name, attr_type in self.mod.StaticObject.__annotations__.items():
            init_f_code.append(f"self.{attr_name} = DATA.{attr_name}")  # if it does not ignore, fix it!
        self.mod.StaticObject.__annotations__['GOAL'] = bool
        if init_f_code:

            full_f_code = '\n    '.join(init_f_code)
            full_code = f"def hct_stf_init(self):\n    {full_f_code}"
            fn = f"{self.tempdir}/hpy_stf_init_{self.mod.StaticObject.__name__}.py"
            open(fn, "w+").write(full_code)
            f_code = compile(full_code, fn, 'exec')
            exec(f_code, self.mod.__dict__)
            self.mod.StaticObject.__init__ = self.mod.__dict__["hct_stf_init"]
            self.mod.StaticObject.__init__.__name__ = "__init__"



        #dump goals and actions
        self.dump_functions(code, 'hpy_etable.py')
        self.dump_functions(goal_code_source, 'hpy_goals.py')

        self.methods_classes.update(self.classes)
        just_classes = list(filter(lambda x: isinstance(x, type), self.methods_classes.values()))

        # plan_or_invariants = hyperc.solve(self.methods_classes[main_goal.name], self.methods_classes, just_classes, DATA)

        plan_or_invariants = self.solver_call(goal=self.methods_classes[main_goal.name],
                                              extra_instantiations=just_classes)
        print("finish")
        
    def finish(self):
        self.stl.calculate_excel()
        dirn = os.path.dirname(self.filename)
        new_dirname = os.path.join(dirn, f"{self.filename.name}_out")
        try:
            mkdir(new_dirname)
        except FileExistsError:
            pass
        new_dirname_forfile = os.path.join(dirn, f"{self.filename.name}_out", str(int(time.time())))
        mkdir(new_dirname_forfile)
        self.stl.write(new_dirname_forfile)

        self.out_filename = os.path.join(new_dirname_forfile, self.filename.name)
        return self.out_filename

    # def call_sequential(self, sequency)
