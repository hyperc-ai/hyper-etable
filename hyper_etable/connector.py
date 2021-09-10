import hyperc.xtj
import openpyxl
import hyper_etable.meta_table
import collections

class Connector:
    def __init__(self, path, mod, has_header=True):
        self.path = path
        self.has_header = has_header
        self.tables = {}
        self.objects = {}
        self.classes = {}
        self.HCT_OBJECTS = {}
        self.mod = mod


class XLSXConnector(Connector):

    def open(self, path, has_header=True):
        super().__init__(self, path, has_header)()
        self.wb_values_only = openpyxl.load_workbook(filename=self.path, data_only=True)
        self.wb_with_formulas = openpyxl.load_workbook(filename=self.path)
        for wb_sheet in self.wb_values_only:
            sheet = wb_sheet.title
            self.tables[sheet] = {}
            py_table_name = hyperc.xtj.str_to_py(f'{sheet}') # warning only sheet in 
            header_map = {}
            header_back_map = {}
            if self.has_header:
                is_header = True
            else:
                is_header = False
            ThisTable = hyper_etable.meta_table.TableElementMeta(f'{py_table_name}_Class', (object,), {'__table_name__': py_table_name, '__xl_sheet_name__': sheet})
            ThisTable.__annotations__ = {'__table_name__': str, 'addidx': int}
            ThisTable.__header_back_map__ = header_back_map
            ThisTable.__user_defined_annotations__ = []
            ThisTable.__default_init__ = {}
            ThisTable.__touched_annotations__ = set()
            ThisTable.__annotations_type_set__ = collections.defaultdict(set)
            self.mod.__dict__[f'{py_table_name}_Class'] = ThisTable
            self.classes[py_table_name] = ThisTable
            self.classes[py_table_name].__qualname__ = f"{self.session_name}.{py_table_name}_Class"
            self.mod.HCT_OBJECTS[py_table_name] = []
            ThisTable.__recid_max__ = 0
            for row in wb_sheet.iter_rows():
                recid = list(row)[0].row
                if ThisTable.__recid_max__ < recid:
                   ThisTable.__recid_max__ = recid
                rec_obj = ThisTable()
                rec_obj.addidx = -1
                if self.has_header:
                    rec_obj.__header_back_map__ = header_back_map
                rec_obj.__recid__ = recid
                rec_obj.__table_name__ += f'[{self.path}]{sheet}_{recid}'
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
                    if self.has_header:
                        column_name = header_map.get(letter, None)
                        #Skip column with empty header bug #176
                        if column_name is None or column_name == "":
                            continue
                    else:
                        column_name = letter
                    if self.has_header:
                        self.objects[py_table_name][recid].__header_back_map__ = header_back_map

                    self.objects[py_table_name][recid].__touched_annotations__.add(column_name)

                    if xl_orig_calculated_value in ['#NAME?', '#VALUE!']:
                        raise Exception(f"We don't support table with error cell ")
                    if (type(xl_orig_calculated_value) == bool or type(xl_orig_calculated_value) == int or type(xl_orig_calculated_value) == str):
                        setattr(self.objects[py_table_name][recid], column_name, xl_orig_calculated_value)
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

    def __str__(self):
        return f'XLSX_FILE_{hyperc.xtj.str_to_py(self.path)}'

class CSVConnector(Connector):

    def __str__(self):
        return f'CSV_FILE_{hyperc.xtj.str_to_py(self.path)}'

class GSheetConnector(Connector):

    def __str__(self):
        return f'GSHEET_{hyperc.xtj.str_to_py(self.path)}'

class MSAPIConnector(Connector):

    def __str__(self):
        return f'MSAPI_{hyperc.xtj.str_to_py(self.path)}'

