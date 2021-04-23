import formulas
import collections
import hyperc.settings
import hyperc.xtj
import schedula
import copy

def get_var_from_cell(cell_str):
    cell = formulas.Parser().ast("="+list(formulas.Parser().ast("=" + cell_str)
                                          [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0][0].attr
    letter = cell['c1'].lower()
    number = cell['r1']
    sheet_name = hyperc.xtj.str_to_py(f"[{cell['excel']}]{cell['sheet']}")
    var_name = f'var_tbl_{sheet_name}__hct_direct_ref__{number}_{letter}'
    return var_name

def formulas_parser(formula_str):
    return formulas.Parser().ast("="+list(formulas.Parser().ast("=" + formula_str)
                                          [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0]

def split_cell(cell_str):
    # return (file, sheet, rec_id , letter) 
    cell = formulas.Parser().ast("="+list(formulas.Parser().ast("=" + cell_str)
                                          [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0][0].attr
    return (cell['excel'], cell['sheet'], cell['r1'], cell['c1'].lower())

class StringLikeVars:
    def __init__(self,rendered_str, args):
        self.rendered_str = rendered_str
        self.args  = args
        self.variables = []
        for arg in self.args:
            if isinstance(arg, str):
                self.variables.append(arg)
            elif isinstance(arg, StringLikeVars):
                self.variables.extend(arg.variables)

    def __str__(self):
        return self.rendered_str

class EtableTranspiler:

    def __init__(self, formula, inputs, output, init_code=None):
        self.formula = formula
        self.inputs = inputs
        self.output = output
        self.init_code = init_code
        if self.init_code is None:
            self.init_code = []
        self.default = schedula.EMPTY
        try:
            self.nodes = formulas.Parser().ast("="+list(formulas.Parser().ast(formula)
                                                        [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0]
        except formulas.errors.FormulaError as e:
            # print(f"Can't parse {v}: {e}")
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
        self.return_var = get_var_from_cell(self.output)
        transpiled_formula_return = self.transpile(self.nodes)
        filename, sheet, recid, letter = split_cell(self.output)
        sheet_name = hyperc.xtj.str_to_py(f"[{filename}]{sheet}")
        self.output_code = []
        self.output_code.append(f'    {self.return_var} = {transpiled_formula_return}')
        self.output_code.append(f'    HCT_STATIC_OBJECT.{sheet_name}_{recid}.{letter} = {self.return_var}')
        self.output_code.append(f'    # side effect with {self.return_var} can be added here')


    def f_selectif(self, *args):
        assert ((len(args)+1) % 2) == 0, "Args in selectif should be odd"
        assert len(args) > 2, "Args should be 3 and more"
        if self.paren_level == 1:
            self.default = args[0]
        ret_var = f'var_tbl_SELECT_IF_{get_var_from_cell(self.output)}_{self.var_counter}'
        self.var_counter += 1
        for idx, arg in enumerate(args):
            if idx % 2 == 0:
                continue
            if idx == 1:
                self.code.append(f"    if {arg}:")
                self.code.append(f"        assert True")
                self.code.append(f"        {ret_var} = {args[idx+1]}")
            else:
                self.code.append(f"    elif {arg}:")
                self.code.append(f"        assert True")
                self.code.append(f"        {ret_var} = {args[idx+1]}")
        self.code.append(f"    else:")
        self.code.append(f"        assert False")


        return ret_var

    def f_and(self, *args):
        if len(args) == 2 and self.paren_level > 1:
            v1 = args[0]
            v2 = args[1]
            return self.save_return(f"({v1} and {v2})", bool)
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
        return self.save_return(StringLikeVars(f"({v1} == {v2})", [v1, v2]), bool)

    def f_ne(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} != {v2})", [v1, v2]), bool)

    def f_add(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} + {v2})", [v1, v2]), int)

    def f_sub(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} - {v2})", [v1, v2]), int)

    def f_mul(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} * {v2})", [v1, v2]), int)

    def f_div(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} // {v2})", [v1, v2]), int)

    def f_lt(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} < {v2})", [v1, v2]), bool)

    def f_gt(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} > {v2})", [v1,v2]), bool)

    def f_le(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} <= {v2})", [v1, v2]), bool)

    def f_ge(self, v1, v2):
        return self.save_return(StringLikeVars(f"({v1} >= {v2})", [v1, v2]), bool)

    def transpile(self, nodes):
        if isinstance(nodes, list):
            ret = ""
            for node in nodes:
                ret = str(self.transpile(node))
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
        return get_var_from_cell(node.attr['name'])

    def save_return(self, ret, type_):
        self.remember_types[ret] = type_
        return ret

class CodeElement:

    def __init__(self):
        self.code_chunk = collections.defaultdict(list)
        self.contion_vars = collections.defaultdict(list)

class FunctionCode:
    def __init__(self, name, parent_name=None):
        self.name = name
        self.parent_name = set()
        if parent_name is not None:
            self.parent_name.add(parent_name)
        self.init = []
        self.operators = []
        self.args = []
        self.selected_cell = []
        self.output = []

    def merge(self, other):
        self.name = f'{self.name}_{other.name}'
        self.init.extend(other.init)
        self.operators.extend(other.operators)
        self.args.extend(other.args)
        self.selected_cell.extend(other.selected_cell)
        self.output.extend(other.output)
        self.parent_name.update(self.parent_name)
    
    # return true if funtions has relation
    def check_relation(self, other):
        return not self.parent_name.isdisjoint(other.parent_name)


    def clean(self):
        found = False
        while not found:
            found = False
            for init in self.init:
                var = init.split('#')[0].split('=')[0].strip()
                for op in self.operators:
                    if var in op:
                        found = True
                        break
                if not found:
                    self.init.remove(init)
                    break

    def __str__(self):
        init = '\n'.join(self.init)
        operators = '\n'.join(self.operators)
        output = '\n'.join(self.output)
        return f'''def {self.name}():
{init}
{operators}
{output}
'''


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
                        code[f'{self.init_code.name}_{ce}'].selected_cell = code_chunk.contion_vars[ce]
                        code[f'{self.init_code.name}_{ce}'].idx = idx
                else:
                    ce = list(code_chunk.code_chunk.keys())[0]
                    self.init_code.operators = code_chunk.code_chunk[ce]
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
        for  c in code.values():
            c.output.extend(self.output_code)
        self.code = code

    def f_selectif(self, *args):
        assert ((len(args)+1) % 2) == 0, "Args in selectif should be odd"
        assert len(args) > 2, "Args should be 3 and more"
        if self.paren_level == 1:
            self.default = args[0]
        ret_var = f'var_tbl_SELECT_IF_{get_var_from_cell(self.output)}_{self.var_counter}'
        self.var_counter += 1
        code_element = CodeElement()
        self.code.append(code_element)
        for idx, arg in enumerate(args):
            if idx % 2 == 0:
                continue
            code_element.code_chunk[f'branch{int((idx-1)/2)}'].append(f"    assert {arg}")
            code_element.code_chunk[f'branch{int((idx-1)/2)}'].append(f"    {ret_var} = {args[idx+1]}")
            code_element.contion_vars[f'branch{int((idx-1)/2)}'].extend(arg.variables)

        return ret_var


class EtableTranspilerBreeder(EtableTranspiler):

    def transtile_node_breeder(self, node):

        if isinstance(node, formulas.tokens.parenthesis.Parenthesis):
            if node.attr["name"] == "(":
                if self.last_node is not None:
                    self.last_node.args_counter = self.args_counter
                self.args_counter = 0
                self.stack.append(self.last_node)
                self.paren_level += 1
            if node.attr["name"] == ")":
                if len(self.stack) == 0:
                    print("ff")
                deleted_node = self.stack.pop() 
                if deleted_node is not None:
                    self.args_counter = deleted_node.args_counter
                    deleted_node.args_counter = 0
                else:
                    self.args_counter = 0
                self.paren_level -= 1
        elif isinstance(node, formulas.tokens.function.Function):
            # if node.attr["name"] == 'SELECTIF' and node.attr['n_args'] > 3:
            #     self.breeder_stop = False
            return 
        elif isinstance(node, formulas.tokens.operator.Separator):
            if node.attr["name"] != ",":
                raise ValueError("Can't support separator %s" % node.attr["name"])
            self.args_counter += 1
            if len(self.stack) == 0:
                return
            if isinstance(self.stack[-1], formulas.tokens.function.Function):
                if self.stack[-1].attr["name"] == 'SELECTIF':
                    if self.args_counter == 3:
                        self.breeder_stop = True
                        #split node list here
                        for n in self.current_nodes:
                            if hasattr(n, 'args_counter'):
                                n.args_counter=0
                        idx = self.current_nodes.index(node)
                        self.breeded_nodes.remove(self.current_nodes)
                        chunk1 = self.current_nodes[0:idx]
                        cut = idx+(self.stack[-1].attr['n_args'] * 2 - (self.args_counter * 2 - 1))
                        chunk1.extend(self.current_nodes[idx+(self.stack[-1].attr['n_args'] * 2 - (self.args_counter * 2 - 1)):])
                        chunk2 = self.current_nodes[0:idx-4]
                        chunk2.extend(self.current_nodes[idx:])
                        self.breeded_nodes.append(chunk1)
                        self.breeded_nodes.append(chunk2)
            return

# breed selectif only
    def traspile_breeder(self, nodes):
        if isinstance(nodes, list):
            for node in nodes:
                self.traspile_breeder(node)
                if self.breeder_stop:
                    return
        else:
            self.transtile_node_breeder(nodes)
            self.last_node = nodes

    def breeder(self):
        self.breeded_nodes.append(self.nodes)
        self.breeder_stop = True
        while self.breeder_stop:
            self.breeder_stop = False
            for nodes in self.breeded_nodes:
                self.current_nodes = nodes
                self.paren_level = 0
                self.args_counter = 0
                self.stack = []
                self.last_node = None
                self.traspile_breeder(nodes)

    def transpile_start(self):
        self.breeded_nodes = []
        self.breeder()
        for nodes in self.breeded_nodes:
            self.nodes = nodes
            super(EtableTranspilerBreeder, self).transpile_start()

    def f_selectif(self, *args):
        assert ((len(args)+1) % 2) == 0, "Args in selectif should be odd"
        assert len(args) > 2, "Args should be 3 and more"
        if self.paren_level == 1:
            self.default = args[0]
        ret_var = f'var_tbl_SELECT_IF_{get_var_from_cell(self.output)}_{self.var_counter}'
        self.var_counter += 1
        for idx, arg in enumerate(args):
            if idx % 2 == 0:
                continue
            if idx == 1:
                self.code.append(f"    assert {arg}")
                self.code.append(f"    {ret_var} = {args[idx+1]}")

        return ret_var
