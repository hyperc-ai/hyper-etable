import formulas
import collections
import hyperc.settings
import hyperc.xtj

def get_var_from_cell(cell):
    letter = cell['c1'].lower()
    number = cell['r1']
    sheet_name = hyperc.xtj.str_to_py(f"[{cell['excel']}]{cell['sheet']}")
    var_name = f'var_tbl_{sheet_name}__hct_direct_ref__{number}_{letter}'
    return var_name

class EtableTranspiler:

    def __init__(self, formula):
        self.formula = formula
        try:
            self.nodes = formulas.Parser().ast("="+list(formulas.Parser().ast(formula['function'].name)
                                                        [1].compile().dsp.nodes.keys())[0].replace(" = -", "=-"))[0]
        except formulas.errors.FormulaError as e:
            # print(f"Can't parse {v}: {e}")
            raise e

    def transpile_start(self):
        self.paren_level = 0
        self.functions = []
        self.last_node = None
        self.function_parens = {}
        self.function_parens_args = collections.defaultdict(list)
        self.code = []
        self.remember_types = {}
        self.return_var = get_var_from_cell(self.formula['outputs'][0])
        self.selectif = False
        return_formula = self.transpile(self.nodes)
        if self.selectif:
            return self.transpile(self.nodes)
        else:
            return f'{self.return_var} = {return_formula}'

    def f_selectif(self, *args):
        self.selectif = True
        counter = 0
        code = []
        for arg in args:
            if counter % 2 == 0:
                code.append(f'        assert True')
            if counter == 1:
                code.append(f'    if ({arg}):')
                code.append(f'        assert True')
            elif counter > 2:
                code.append(f'    elif ({arg}):')
                code.append(f'        assert True')
            counter += 1
        code.append('    else:')
        code.append(f'        assert False')
        return code

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
        return self.save_return(f"({v1} == {v2})", bool)

    def f_ne(self, v1, v2):
        return self.save_return(f"({v1} != {v2})", bool)

    def f_add(self, v1, v2):
        return self.save_return(f"({v1} + {v2})", int)

    def f_sub(self, v1, v2):
        return self.save_return(f"({v1} - {v2})", int)

    def f_mul(self, v1, v2):
        return self.save_return(f"({v1} * {v2})", int)

    def f_div(self, v1, v2):
        return self.save_return(f"({v1} // {v2})", int)

    def f_lt(self, v1, v2):
        return self.save_return(f"({v1} < {v2})", bool)

    def f_gt(self, v1, v2):
        return self.save_return(f"({v1} > {v2})", bool)

    def f_le(self, v1, v2):
        return self.save_return(f"({v1} <= {v2})", bool)

    def f_ge(self, v1, v2):
        return self.save_return(f"({v1} >= {v2})", bool)

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
        return get_var_from_cell(node.attr)

    def save_return(self, ret, type_):
        self.remember_types[ret] = type_
        return ret
