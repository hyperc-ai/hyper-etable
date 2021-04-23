"""
Convert the HyperC objects back to Excel spreadsheet
"""

import hyperc.xtj
from collections import defaultdict
import schedula as sh
from formulas.cell import CellWrapper
import os.path


def to_dict(self):
    nodes = {
        k: d['value']
        for k, d in self.dsp.default_values.items()
        if not isinstance(k, sh.Token)
    }
    nodes = {
        k: isinstance(v, str) and v.startswith('=') and '="%s"' % v or v
        for k, v in nodes.items() if v != [[sh.EMPTY]]
    }
    for d in self.dsp.function_nodes.values():
        fun = d['function']
        if isinstance(fun, CellWrapper):
            nodes.update(dict.fromkeys(d['outputs'], fun.__name__))
    return nodes


class SpileTrancer:
    def __init__(self, filename, xl_model, static_objects, table_records=None):
        self.static_objects = static_objects
        self.filename = filename
        self.xl_model = xl_model
        xl_model.finish()
        # self.xl_dict = xl_model.to_dict()
        self.xl_dict = to_dict(xl_model)
    
    def gen_xl_addr(self, filename, sheetname, letter, rownum):
        filename = os.path.basename(filename)
        return f"'[{filename}]{sheetname}'!{letter}{rownum}".upper()
    
    def calculate_excel(self):
        "Return full xlsx"
        # First, collect types of annotations

        attr_names_by_class = defaultdict(list)
        for key, val in sorted(type(self.static_objects).__annotations__.items()):
            if not hasattr(val, "__table_name__"):
                continue
            attr_names_by_class[val].append(key)
        
        all_inputs = {}  # this dict will rewrite all inputs
        
        for cls_, cells in attr_names_by_class.items():
            for cell in cells:
                rownum = int(cell.split("_")[-1])
                sheetname = cls_.__xl_sheet_name__
                for letter, type_ in cls_.__annotations__.items():
                    if len(letter) > 3:
                        continue  # ignore trash?
                    xl_cell_ref = self.gen_xl_addr(self.filename, sheetname, letter, rownum)

                    # First, check what we currently have at this cell
                    if (type(self.xl_dict[xl_cell_ref]) == str and 
                            self.xl_dict[xl_cell_ref].upper().startswith("=SELECTIF")):
                        # Selectif -> replace default value
                        cellvalue = getattr(getattr(self.static_objects, cell), letter)
                        orig_cell = self.xl_dict[xl_cell_ref]
                        if type_ == str:
                            cellvalue = f'"{cellvalue}"'
                        # TODO: tokenize, rewrite, re-render
                        cellvalue = f"=SELECTIF({cellvalue}, {orig_cell.split(',', 1)[1]}"
                        all_inputs[xl_cell_ref] = cellvalue
                    elif (type(self.xl_dict[xl_cell_ref]) == str and 
                            self.xl_dict[xl_cell_ref].upper().startswith("=")):
                        pass
                    else:  # raw value? just write what we have
                        all_inputs[xl_cell_ref] = getattr(getattr(self.static_objects, cell), letter)

        self.xl_model.calculate(inputs=all_inputs)

        # TODO: assert and double-check calculations
    
    def write(self, dir):
        self.xl_model.write(dirpath=dir)




