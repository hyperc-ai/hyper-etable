import formulas
import collections
import hyperc.settings
import hyperc.xtj
import schedula
import copy
import random
import string
import hyper_etable.type_mapper

def split_cell(cell_str):
    # return (file, sheet, rec_id , letter)
    cell = formulas.Parser().ast("="+list(formulas.Parser().ast("=" + cell_str)
                                          [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0][0].attr
    if (cell['r1'] != cell['r2']) or (cell['c1'] != cell['c2']):
        return (cell['excel'], cell['sheet'], [int(cell['r1']), int(cell['r2'])], [cell['c1'].lower(), cell['c2'].lower()])
    else:
        return (cell['excel'], cell['sheet'], int(cell['r1']), cell['c1'].lower())


def get_var_from_cell(cell_str):
    cell = formulas.Parser().ast("="+list(formulas.Parser().ast("=" + cell_str)
                                          [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0][0].attr
    letter = cell['c1'].lower()
    number = cell['r1']
    sheet_name = hyperc.xtj.str_to_py(f"[{cell['excel']}]{cell['sheet']}")
    var_name = f'var_tbl_{sheet_name}__hct_direct_ref__{number}_{letter}'
    return var_name

class StringLikeConstant(object):

    @staticmethod
    def new(var_map, var):
        if var in var_map:
            return var_map[var]
        else:
            return StringLikeConstant(var_map, var)

    def __init__(self, var_map, var):
        self.var = var
        self.types = set()
        self.types.add(type(var))
        self.type_group_set = set()
        self.var_map = var_map
        self.new_type_group(var_map)
        self.var_map[self.var] = self
        self.variables = set()
        self.variables.add(self)

    def __str__(self):
        return str(self.var)

    def __hash__(self):
        return hash(self.var)

    def set_types(self, type):
        if isinstance(type, set):
            self.types.update(type)
        else:
            self.types.add(type)

    def new_type_group(self, var_map):
        # random duplicateless Generator
        loop = True
        rnd_len = 1
        while loop:
            loop = False
            type_group = 'type_group_'+''.join(random.choices(string.ascii_uppercase + string.digits, k=rnd_len))
            for k in var_map:
                if var_map[k].type_group == type_group:
                    loop = True
            if not loop:
                self.type_group = type_group
                self.type_group_set.add(type_group)
            rnd_len += 1

class StringLikeVariable:

    @staticmethod
    def new(var_map, cell_str=None, filename=None, sheet=None, letter=None, number=None, var_str=None):
        if var_str in var_map:
            return var_map[var_str]
        else:
            return StringLikeVariable(
                var_map=var_map, cell_str=cell_str, filename=filename, sheet=sheet, letter=letter, number=number,
                var_str=var_str)

    def __init__(self, var_map, cell_str = None, filename=None, sheet=None, letter=None, number=None, var_str=None):
        if cell_str is None:
            self.filename = filename
            self.sheet = sheet
            self.letter = letter
            self.number = int(number)
        else:
            self.filename, self.sheet, self.number, self.letter = split_cell(cell_str)
        if isinstance(self.number, list):
            self.is_range = True
        else:
           self.is_range = False

        self.var_str = var_str
        if self.var_str is None:
            sheet_name = hyperc.xtj.str_to_py(f"[{self.filename}]{self.sheet}")
            if self.is_range:
                self.var_str = f'var_tbl_{sheet_name}__range_{self.number[0]}_{self.number[1]}_{self.letter[0]}'
            else:
                self.var_str = f'var_tbl_{sheet_name}__hct_direct_ref__{self.number}_{self.letter}'
        self.types = set()
        self.type_group_set = set()
        self.var_map = var_map
        self.new_type_group(var_map)
        self.var_map[self.var_str] = self
        self.variables = set()
        self.variables.add(self)

    def get_excel_format(self):
        return f"'[{self.filename}]{self.sheet}'!{self.letter.upper()}{self.number}"

    def __str__(self):
        return self.var_str
    
    def __hash__(self):
        self.hash = hash(str(self.var_str))
        return self.hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def set_types(self,type):
        if isinstance(type, set):
            self.types.update(type)
        else:
            self.types.add(type)

    def new_type_group(self, var_map):
        # random duplicateless Generator
        loop = True
        rnd_len = 1
        while loop:
            loop = False
            type_group = 'type_group_'+''.join(random.choices(string.ascii_uppercase + string.digits, k=rnd_len))
            for k in var_map:
                if var_map[k].type_group == type_group:
                    loop = True
            if not loop:
                self.type_group = type_group
                self.type_group_set.add(type_group)
            rnd_len += 1

def formulas_parser(formula_str):
    return formulas.Parser().ast("="+list(formulas.Parser().ast("=" + formula_str)
                                          [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0]




class StringLikeVars:
    def __init__(self,rendered_str, args, operator):
        self.rendered_str = rendered_str
        self.args  = args
        self.variables = set()
        for arg in self.args:
            if isinstance(arg, StringLikeVars):
                self.variables.update(arg.variables)
            else:
                self.variables.add(arg)
        self.operator = operator
    
    def extend(self, args):
        for arg in args:
            if isinstance(arg, str):
                self.variables.add(arg)
            elif isinstance(arg, StringLikeVars):
                self.variables.update(arg.variables)

    def __str__(self):
        return str(self.rendered_str)

    def __hash__(self):
        return hash(str(self.rendered_str))

class EtableTranspiler:

    def __init__(self, formula, inputs, output, var_mapper, table_type_mapper, init_code=None):
        self.var_mapper = var_mapper
        self.table_type_mapper = table_type_mapper
        if formula.endswith("<0>"):
            formula = formula[:-3]
        self.formula = formula
        self.inputs = inputs
        self.output = output
        self.init_code = init_code
        if self.init_code is None:
            self.init_code = {}
        self.default = schedula.EMPTY
        self.args = set()
        try:
            self.nodes = formulas.Parser().ast("="+list(formulas.Parser().ast(formula)
                                                        [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0]
        except formulas.errors.FormulaError as e:
            # print(f"Can't parse {formula}: {e}")
            raise e

    def transpile_start(self):
        self.var_counter = 0
        self.paren_level = 0
        self.functions = []
        self.last_node = None
        self.function_parens = {}
        self.function_parens_args = collections.defaultdict(list)
        self.code = []
        self.remember_types = {}
        self.return_var = StringLikeVariable.new(var_map = self.var_mapper, cell_str=self.output)
        transpiled_formula_return = self.transpile(self.nodes)
        filename, sheet, recid, letter = split_cell(self.output)
        sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}")
        self.output_code = []
        self.output_code.append(f'{self.return_var} = {transpiled_formula_return}')
        self.output_code.append(f'HCT_STATIC_OBJECT.{sheet_name}_{recid}.{letter} = {self.return_var}')
        self.output_code.append(f'# side effect with {self.return_var} can be added here')

    def f_and(self, *args):
        if len(args) == 2 and self.paren_level > 1:
            v1 = args[0]
            v2 = args[1]
            return self.save_return(StringLikeVars(f"({v1} and {v2})", [v1, v2]), bool)
        elif self.paren_level == 1:
            for what in args:
                if what.startswith("(") and what.endswith(")"):
                    what = what[1:-1]
                self.code.append(["assert", what,
                                  f"# {self.s_formula} from {self.cur_tbl} (action {self.action['name']})"])
            return "True"
        else:
            raise TypeError("AND() only supports 2 arguments if used in complex formula")

    def f_eq(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} == {v2})", [v1, v2], "=="), bool)

    def f_ne(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} != {v2})", [v1, v2], "!="), bool)

    def f_add(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} + {v2})", [v1, v2], "+"), int)

    def f_sub(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} - {v2})", [v1, v2], "-"), int)

    def f_mul(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} * {v2})", [v1, v2], "*"), int)

    def f_div(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} // {v2})", [v1, v2], "//"), int)

    def f_lt(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} < {v2})", [v1, v2], "<"), bool)

    def f_gt(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} > {v2})", [v1, v2], ">"), bool)

    def f_le(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} <= {v2})", [v1, v2], "<="), bool)

    def f_ge(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} >= {v2})", [v1, v2], ">="), bool)
    
    def f_true(self):
        return self.save_return(StringLikeVars("True", [StringLikeConstant.new(var_map=self.var_mapper,var=True)], "" ), bool)

    def transpile(self, nodes):
        if isinstance(nodes, list):
            ret = ""
            for node in nodes:
                ret = self.transpile(node)
                pass
            return ret
        else:
            ret = self.transpile_node(nodes)
            self.last_node = nodes
            return ret

    def transpile_node(self, node):
        if isinstance(node, formulas.tokens.operand.Range):
            ret = self.transpile_range(node)
            if self.paren_level in self.function_parens:
                self.function_parens_args[self.paren_level].append(ret)
            return ret
        elif isinstance(node, formulas.tokens.parenthesis.Parenthesis):
            if node.attr["name"] == "(":
                self.paren_level += 1
#                 print("Opened paren level", self.paren_level)
                if isinstance(self.last_node, formulas.tokens.function.Function):
                    #                     print("Storing last function:", self.paren_level, self.last_node)
                    self.function_parens[self.paren_level] = "f_"+self.last_node.attr["name"].lower()
                else:
                    self.function_parens[self.paren_level] = "<TBD>"
            else:
                #                 print("Paren close level", self.paren_level)
                if self.paren_level in self.function_parens:
                    #                     print(self.function_parens[self.paren_level].lower(), self.function_parens_args[self.paren_level])
                    ret = getattr(self, self.function_parens[self.paren_level])(
                        *self.function_parens_args[self.paren_level])
                    self.function_parens_args[self.paren_level] = []
                    self.paren_level -= 1
                    self.function_parens_args[self.paren_level].append(ret)
                    return ret
                self.paren_level -= 1
            assert self.paren_level >= 0, "Too many closing parenthesis! %s" % self.paren_level
            return node.attr["name"]  # TODO: WARNING: this is wrong??
        elif isinstance(node, formulas.tokens.function.Function):
            self.functions.append("f_"+node.attr["name"])
            return node.attr["name"].lower()
        elif isinstance(node, formulas.tokens.operator.Separator):
            if node.attr["name"] != ",":
                raise ValueError("Can't support separator %s" % node.attr["name"])
            return ", "
        elif isinstance(node, formulas.tokens.operand.Number):
            isint = True
            if node.attr["name"].lower() == "true":  # FIX HERE: need to check inference
                ret = True
                isint = False
            elif node.attr["name"].lower() == "false":
                ret = False
                isint = False
            if isint:
                ret = int(node.attr["name"])
            ret = StringLikeConstant.new(var_map=self.var_mapper, var=ret)
            if self.paren_level in self.function_parens:
                self.function_parens_args[self.paren_level].append(ret)
            return ret
        elif isinstance(node, formulas.tokens.operand.String):
            isint = True
            if node.attr["name"].lower() == "true":  # FIX HERE: need to check inference
                ret = True
                isint = False
            elif node.attr["name"].lower() == "false":
                ret = False
                isint = False
            if isint:
                ret = node.attr["expr"]
            ret = StringLikeConstant.new(var_map=self.var_mapper, var=ret)
            if self.paren_level in self.function_parens:
                self.function_parens_args[self.paren_level].append(ret)
            return ret

        elif isinstance(node, formulas.tokens.operator.OperatorToken):
            if node.attr["name"] == "=":
                self.function_parens[self.paren_level] = 'f_eq'
                return None
            elif node.attr["name"] == "+":
                self.function_parens[self.paren_level] = 'f_add'
                return None
            elif node.attr["name"] == "-":
                self.function_parens[self.paren_level] = 'f_sub'
                return None
            elif node.attr["name"] == "*":
                self.function_parens[self.paren_level] = 'f_mul'
                return None
            elif node.attr["name"] == "/":
                self.function_parens[self.paren_level] = 'f_div'
                return None
            elif node.attr["name"] == "<":
                self.function_parens[self.paren_level] = 'f_lt'
                return None
            elif node.attr["name"] == ">":
                self.function_parens[self.paren_level] = 'f_gt'
                return None
            elif node.attr["name"] == "<=":
                self.function_parens[self.paren_level] = 'f_le'
                return None
            elif node.attr["name"] == ">=":
                self.function_parens[self.paren_level] = 'f_ge'
                return None
            elif node.attr["name"] == "<>":
                self.function_parens[self.paren_level] = 'f_ne'
                return None
            else:
                raise NotImplementedError("Not Implemented Operator: %s" % repr(node))
        else:
            raise NotImplementedError("Not Implemented: %s" % repr(node))

    def transpile_range(self, node: formulas.tokens.operand.Range):
        if not 'sheet' in node.attr:
            raise formulas.errors.FormulaError(f"Formula reference without row ID")
        # return node.attr
        return StringLikeVariable.new(var_map=self.var_mapper, cell_str=node.attr['name'])

    def save_return(self, ret, type_=None):
        self.remember_types[ret] = type_
        for arg in ret.args:
            if not isinstance(arg, str):
                continue
            if 'var_tbl_' not in arg:
                continue
            self.init_code.args.add(arg)

        if ret.operator in ['-', '+', '/', '*', '>', '<', '<=', '>=']:
            for var in ret.variables:
                var.set_types(int)


        # set neighbour
        if len(ret.variables) > 1 :
            for var1 in ret.variables:
                for var2 in ret.variables:
                    var1.type_group_set.update(var2.type_group_set)
                    var2.type_group_set.update(var1.type_group_set)
        
        # create type group mapper
        for var in ret.variables:
            if var.type_group not in self.table_type_mapper:
                self.table_type_mapper[var.type_group] = hyper_etable.type_mapper.TypeMapper(
                    group=var.type_group_set, name=var.type_group, types=var.types)

        return ret
   

class CodeElement:

    def __init__(self):
        self.code_chunk = collections.defaultdict(list)
        self.contion_vars = collections.defaultdict(list)
        self.sync_cells = collections.defaultdict(set)
        self.all_vars = collections.defaultdict(list)

class FunctionCode:
    def __init__(self, name, parent_name=None, is_goal=False):
        self.name = name
        self.parent_name = set()
        if parent_name is not None:
            self.parent_name.add(parent_name)
        self.init = {}
        self.operators = []
        self.args = set()
        self.function_args = {}
        self.selected_cell = set()
        self.sync_cell = set()
        self.output = []
        self.collapsed = False
        self.selectable = False
        self.effect_vars = set()
        self.is_goal = is_goal

    def merge(self, other):
        self.name = f'{self.name}_{other.name}'
        self.init.extend(other.init)
        self.operators.extend(other.operators)
        self.args.update(other.args)
        self.effect_vars.update(other.effect_vars)
        self.selected_cell.update(other.selected_cell)
        self.sync_cell.update(other.sync_cell)
        self.output.extend(other.output)
        self.parent_name.update(other.parent_name)
        if other.selectable:
            self.selectable = True

    def collapse(self):
        if self.collapsed:
            return
        collapsed_code = []
        collapsed_code.extend(self.init.values())
        collapsed_code.extend(self.operators)
        collapsed_code.extend(self.output)
        self.init={}
        self.operators = []
        self.output = collapsed_code

    def glue(self,other):
        self.collapse()
        other.collapse()
        self.name = f'{self.name}_{other.name}'
        self.output = other.output + self.output
        self.args.update(other.args)
        self.function_args.update(other.function_args)
        self.effect_vars.update(other.effect_vars)
        self.selected_cell.update(other.selected_cell)
        self.sync_cell.update(other.sync_cell)
        self.parent_name.update(other.parent_name)
        if other.selectable:
            self.selectable = True

    def clean(self):
        code = ''.join(self.operators) +''.join(self.output)
        for init_var in list(self.init.keys()):
            if '####comment####' == init_var:
                continue
            if init_var not in code:
                del self.init[init_var]


    def gen_not_hasattr(self):
        not_hasattrs = []
        for eff_var in self.effect_vars:
            py_table_name = hyperc.xtj.str_to_py(f'[{eff_var.filename}]{eff_var.sheet}')
            not_hasattrs.append(
                f'assert HCT_STATIC_OBJECT.{py_table_name}_{eff_var.number}.{eff_var.letter}_not_hasattr == True')
        return "\n    ".join(not_hasattrs)

    def __str__(self):
        if_not_hasattr = ""
        stack_code = []
        if not self.is_goal:
            if self.selectable:
                stack_code.append('stack_drop()')
            else:
                if_not_hasattr = f'\n    {self.gen_not_hasattr()}'
                for eff_var in self.effect_vars:
                    py_table_name = hyperc.xtj.str_to_py(f'[{eff_var.filename}]{eff_var.sheet}')
                    stack_code.append(
                    f'stack_add(HCT_STATIC_OBJECT.{py_table_name}_{eff_var.number},"{eff_var.letter}")')
        stack_code = '\n    '.join(stack_code)

        function_args = ', '.join([f'{k}: {v}' for k, v in self.function_args.items()])
        if self.collapsed:
            operators = '\n    '.join(self.operators)
            return f'''def {self.name}({function_args}):{if_not_hasattr}
    {operators}
    {stack_code}
'''
        else:
            init = '\n    '.join(self.init.values())
            operators = '\n    '.join(self.operators)
            output = '\n    '.join(self.output)
            return f'''def {self.name}({function_args}):{if_not_hasattr}
    {init}
    {operators}
    {output}
    {stack_code}
'''

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

class EtableTranspilerEasy(EtableTranspiler):

    def transpile_start(self):
        super(EtableTranspilerEasy, self).transpile_start()
        code = {}
        for idx, code_chunk in enumerate(self.code):
            if isinstance(code_chunk, CodeElement):
                if len(code_chunk.code_chunk) > 1:
                    for ce in code_chunk.code_chunk:
                        code[f'{self.init_code.name}_{ce}'] = FunctionCode(
                            name=f'{self.init_code.name}_{ce}', parent_name=self.init_code.name)
                        code[f'{self.init_code.name}_{ce}'].init = copy.copy(self.init_code.init)
                        code[f'{self.init_code.name}_{ce}'].operators = code_chunk.code_chunk[ce]
                        code[f'{self.init_code.name}_{ce}'].selected_cell = set(code_chunk.contion_vars[ce])
                        code[f'{self.init_code.name}_{ce}'].sync_cell.update(code_chunk.sync_cells[ce])
                        code[f'{self.init_code.name}_{ce}'].args.update(code_chunk.all_vars)
                        code[f'{self.init_code.name}_{ce}'].idx = idx
                        code[f'{self.init_code.name}_{ce}'].selectable = True
                else:
                    ce = list(code_chunk.code_chunk.keys())[0]
                    self.init_code.operators = code_chunk.code_chunk[ce]
                    self.init_code.selected_cell = set(code_chunk.contion_vars[ce])
                    self.init_code.sync_cell.update(code_chunk.sync_cells[ce])
                    self.init_code.args.update(code_chunk.all_vars[ce])
                    self.init_code.selectable = True
            else:
                self.init_code.operators.append(code_chunk)
        if (len(code) > 0):
            for branch_name in code:
                code[branch_name].operators = self.init_code.operators[0: idx] + code[branch_name].operators
                code[branch_name].operators.extend(self.init_code.operators[idx:])
                code[branch_name].clean()
        else:
            code[self.init_code.name] = self.init_code
            code[self.init_code.name].clean()
        for c in code.values():
            c.output.extend(self.output_code)
            c.effect_vars.add(self.return_var)
        self.code = code

    def f_selectfromrange(self, range):
        assert self.paren_level == 1, "only parent_level 1 is support for selectfromrange"
        range.var_str = f'{range.var_str}_{self.var_counter}'
        self.var_counter += 1
        # select_var = StringLikeVariable.new(
        #     var_map=self.var_mapper, cell_str=range.attr['name'])
        # select_var.var_str
        self.init_code.function_args[range] = hyperc.xtj.str_to_py(f'[{range.filename}]{range.sheet}')
        ret_var = StringLikeVariable.new(
            var_map=self.var_mapper, cell_str=self.output,
            var_str=f'var_tbl_SELECTFROMRANGE_{get_var_from_cell(self.output)}_{self.var_counter}')
        self.var_counter += 1
        self.init_code.init[ret_var] = f'{ret_var} = {range}.{range.letter[0]}'
        return ret_var

    # takeif(default_value, precondition_1, effect_1, sync_cell_1, precondition_2, effect_2, sync_cell_2, .....
    def f_takeif(self, *args):
        assert self.paren_level == 1, "Nested TAKEIF() is not supported"
        assert ((len(args)-1) % 3) == 0, "Args in TAKEIF() should be multiple of three plus one"
        assert len(args) > 3, "TAKEIF() args should be 4 and more"
        if self.paren_level == 1:
            self.default = args[0]
        ret_var = StringLikeVariable.new(
            var_map=self.var_mapper, cell_str=self.output,
            var_str=f'var_tbl_TAKEIF_{get_var_from_cell(self.output)}_{self.var_counter}')
        ret_expr = StringLikeVars(ret_var, args, "takeif")
        self.var_counter += 1
        code_element = CodeElement()
        self.code.append(code_element)
        part = 0
        for a_condition, a_value, a_syncon in divide_chunks(args[1:], 3):  # divinde by 3 elements after first
            code_element.code_chunk[f'branch{part}'].append(f"assert {a_condition} == True")
            code_element.code_chunk[f'branch{part}'].append(f"{ret_expr} = {a_value}")

            self.save_return(
                StringLikeVars(
                    f"{ret_expr} = {a_value}", [ret_var, a_value],
                    "="))
            code_element.sync_cells[f'branch{part}'].add(a_syncon)
            code_element.contion_vars[f'branch{part}'].extend(a_condition.variables)
            code_element.all_vars[f'branch{part}'].extend(a_condition.variables)
            code_element.all_vars[f'branch{part}'].extend(a_value.variables)
            part += 1

        return ret_expr
    
    f_selectif = f_takeif
