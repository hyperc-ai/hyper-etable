import hyperc.util
import hyper_etable.etable_transpiler
import os
import collections

class PlainCell:
    def __init__(self, filename, sheet, letter, number):
        self.directory = os.path.dirname(str(filename))
        self.filename = os.path.basename(str(filename))
        self.sheet = sheet
        self.letter = letter.upper()
        self.number = int(number)

    def __hash__(self):
        # return hash(self.filename) & hash(self.sheet) & hash(self.letter) & hash(self.number)
        return hash(str(self).upper())

    def __str__(self):
        return f"'[{self.filename}]{self.sheet}'!{self.letter}{self.number}"

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self) -> str:
        return f"<PlainCell>{self}"

class PlainCellRange:
    def __init__(self, filename, sheet, letter, number):
        self.directory = os.path.dirname(str(filename))
        self.filename = os.path.basename(str(filename))
        self.sheet = sheet
        assert isinstance(letter, list)
        self.letter = [l.upper() for l in letter] # is list
        assert isinstance(number, list)
        self.number = [int(n) for n in number]

    def __hash__(self):
        return hash(str(self).upper())

    def __str__(self):
        return f"'[{self.filename}]{self.sheet}'!{self.letter[0].upper()}{self.number[0]}:{self.letter[1].upper()}{self.number[1]}"

    def __eq__(self, other):
        return hash(self) == hash(other)

class PlainCellNamedRange:
    def __init__(self, filename, sheet, name, column_name=None, this_row = False):
        self.directory = os.path.dirname(str(filename))
        self.filename = os.path.basename(str(filename))
        self.sheet = sheet
        self.name = name # range or table named_range
        self.column_name = column_name
        self.this_row = this_row

    def __hash__(self):
        return hash(str(self).upper())

    def __str__(self):
        if self.column_name is None:
            return f"'[{self.filename}]{self.sheet}'!{self.name}"
        elif self.this_row:
            return f"'[{self.filename}]{self.sheet}'!{self.name}[[#THIS ROW],[{self.column_name}]]"
        else:
            return f"'[{self.filename}]{self.sheet}'!{self.name}[{self.column_name}]"

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f"<PlainCellNamedRange>{self}"

class RangeResolver:
    def __init__(self, filename, workbook):
        self.wb_values_only = workbook
        self.directory = os.path.dirname(str(filename))
        self.filename = os.path.basename(str(filename))
        self.table_collums = {}
        self.tables = {}
        self.cell_to_table = collections.defaultdict(set)
        for ws in self.wb_values_only.worksheets:
            for t in ws.tables.values():
                _, _, unpak_range_row, unpak_range_column = hyper_etable.etable_transpiler.split_cell(
                    f"'[file]sheet'!{t.ref}")
                # unpak_range_row[0]+1 - filter header. Header have all named tables 
                self.tables[t.displayName.upper()] = PlainCellRange(self.filename, ws.title, unpak_range_column, [
                                                            unpak_range_row[0]+1, unpak_range_row[1]])
                for c in t.tableColumns:
                    _, _, unpak_range_row, unpak_range_column = hyper_etable.etable_transpiler.split_cell(
                        f"'[file]sheet'!{t.ref}")
                    letter_next = unpak_range_column[0]
                    idx = 1
                    while idx != c.id:
                        letter_next = hyperc.util.letter_index_next(letter=letter_next).upper()
                        idx += 1
                    self.table_collums[PlainCellNamedRange(self.filename, ws.title, t.name.upper(), c.name.upper())] = PlainCellRange(
                        self.filename, ws.title, [letter_next.upper(), letter_next.upper()], [unpak_range_row[0]+1, unpak_range_row[1]])
                    

        for df in self.wb_values_only.defined_names.definedName:
            if df.type == 'ERROR' or df.attr_text == '#REF!':
                continue
            _, _, number, letter = hyper_etable.etable_transpiler.split_cell(df.attr_text)
            self.table_collums[PlainCellNamedRange(self.filename, ws.title, df.name)] = PlainCellRange(
                self.filename, ws.title, letter, number)
            self.tables[df.name] = PlainCellRange(self.filename, ws.title, letter, number)

        for table, n_range in self.tables.items():
            for cell in self.gen_cells_from_range(n_range):
                self.cell_to_table[cell].add(table)
        pass

    def gen_cells_from_range(self, n_range):
        ret = []
        letter_stop = n_range.letter[1]
        letter_next = n_range.letter[0]
        for number in range(n_range.number[0], n_range.number[1]+1, 1):
            while letter_stop != letter_next:
                ret.append(PlainCell(filename=n_range.filename, sheet=n_range.sheet, letter=letter_next, number=number))
                letter_next = hyperc.util.letter_index_next(letter=letter_next).upper()
            ret.append(PlainCell(filename=n_range.filename, sheet=n_range.sheet, letter=letter_next, number=number))
        return ret



    def replace_named_ranges(self, formula):
        formula_ret = formula
        for named_range, simple_range in self.table_collums.items():
            if named_range.column_name is None:
                formula_ret = formula_ret.replace(
                    f'{named_range.name.upper()}[#ALL]',
                    f'{simple_range.letter[0]}{simple_range.number[0]}:{simple_range.letter[1]}{simple_range.number[1]}',
                    99)
                formula_ret = formula_ret.replace(
                    f'{named_range.name.upper()}',
                    f'{simple_range.letter[0]}{simple_range.number[0]}:{simple_range.letter[1]}{simple_range.number[1]}',
                    99)
            else:
                formula_ret = formula_ret.replace(
                    f'{named_range.name.upper()}[{named_range.column_name.upper()}]',
                    f'{simple_range.letter[0]}{simple_range.number[0]}:{simple_range.letter[1]}{simple_range.number[1]}',
                    99)
                formula_ret = formula_ret.replace(
                    f'{named_range.name.upper()}[[#THIS ROW],[{named_range.column_name.upper()}]]',
                    f'{simple_range.letter[0]}{simple_range.number[0]}:{simple_range.letter[1]}{simple_range.number[1]}',
                    99)
        return formula_ret

    def get_named_range_by_simple_range(self, simple_range_required):
        for named_range, simple_range in self.table_collums.items():
            if simple_range == simple_range_required:
                return (named_range, simple_range)
        return (None, None)

    def get_cell_range_by_name(self, filename, sheet, name):
        key = PlainCellNamedRange(filename, sheet, name)
        ret =  self.table_collums.get(key, None)
        return ret

    def get_table_by_cell(self, cell):
        return self.cell_to_table.get(cell, None)

    def get_range_name_by_cell(self, cellname):
        filename = cellname.filename
        sheet = cellname.sheet
        row = cellname.number
        column = cellname.letter
        #collect tables
        #extract collums
        table_collums = {}
        for filename_n, sheet_n, table_name, column_name in self.table_collums:
            column_n, row_n = self.table_collums[(filename_n, sheet_n, table_name, column_name)]
            if filename == filename_n and sheet == sheet_n:
                if column_n[0] != column.upper():
                    continue
                if not(row >= row_n[0] and row <= row_n[1]):
                    continue
                return f'!{table_name}[{column_name}]'

        for df in self.wb_values_only.defined_names.definedName:
            filename_n, sheet_n, row_n, column_n = hyper_etable.etable_transpiler.split_cell(df.attr_text)
            if filename == filename_n and sheet == sheet_n:
                if (column_n, list):
                    letter_stop = column_n[1]
                    letter_next = column_n[0]
                    found = False
                    while letter_next != letter_stop:
                        if letter_next == column:
                            found = True
                            break
                        letter_next = hyperc.util.letter_index_next(letter=letter_next).upper()
                    else:
                        if letter_next == column:
                            found = True
                    if not found:
                        continue
                elif column_n != column:
                    continue
                if isinstance(row_n, list):
                    if not(row >= row_n[0] and row <= row_n[1]):
                        continue
                elif row != row_n:
                    continue
                return df.name
        return None
