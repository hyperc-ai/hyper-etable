import hyperc.xtj
import openpyxl
import hyper_etable.meta_table
import hyper_etable.ms_api
import collections
import io
import googleapiclient.discovery
import googleapiclient.http
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import openpyxl
import pathlib
import requests

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
 
    def __init__(self, path, mod, has_header=True):
        super().__init__(path, mod, has_header)
        self.wb_values_only = None

    def load(self):
        self.wb_values_only = openpyxl.load_workbook(filename=self.path, data_only=True)
        self.wb_with_formulas = openpyxl.load_workbook(filename=self.path)
        for wb_sheet in self.wb_values_only:
            sheet = wb_sheet.title
            self.tables[sheet] = {}
            py_table_name = hyperc.xtj.str_to_py(f'{sheet}') # warning only sheet in 
            header_map = {}
            header_back_map = {}
            header_name_map = {} # map python name to true name
            if self.has_header:
                is_header = True
            else:
                is_header = False
            ThisTable = hyper_etable.meta_table.TableElementMeta(f'{py_table_name}_Class', (object,), {'__table_name__': py_table_name, '__xl_sheet_name__': sheet})
            ThisTable.__annotations__ = {'__table_name__': str, 'addidx': int}
            ThisTable.__header_back_map__ = header_back_map
            ThisTable.__header_name_map__ = header_name_map
            ThisTable.__user_defined_annotations__ = []
            ThisTable.__default_init__ = {}
            ThisTable.__touched_annotations__ = set()
            ThisTable.__annotations_type_set__ = collections.defaultdict(set)
            ThisTable.__connector__ = self
            self.mod.__dict__[f'{py_table_name}_Class'] = ThisTable
            self.classes[py_table_name] = ThisTable
            self.classes[py_table_name].__qualname__ = f"{self.mod.__name__}.{py_table_name}_Class"
            self.mod.HCT_OBJECTS[py_table_name] = []
            self.HCT_OBJECTS[py_table_name] = self.mod.HCT_OBJECTS[py_table_name]
            self.objects[py_table_name]={}
            ThisTable.__recid_max__ = 0
            for row in wb_sheet.iter_rows():
                recid = list(row)[0].row
                if ThisTable.__recid_max__ < recid:
                   ThisTable.__recid_max__ = recid
                rec_obj = ThisTable()
                rec_obj.addidx = -1
                if self.has_header:
                    rec_obj.__header_back_map__ = header_back_map
                    rec_obj.__header_name_map__ = header_name_map
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
                        header_name_map[hyperc.xtj.str_to_py(xl_orig_calculated_value)] = xl_orig_calculated_value
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

    def save(self, out_file=None):
        """Save objects into XLSX file"""
        if out_file is None:
            out_file = self.path
        if self.wb_values_only is None:
            self.wb_with_formulas = openpyxl.Workbook()

        out_dir = pathlib.Path(out_file).parent
        try:
            os.mkdir(out_dir)
        except FileExistsError:
            pass
        for table in self.mod.HCT_OBJECTS.values():
            for row in table:
                sheet_name = row.__xl_sheet_name__
                recid = row.__recid__
                for attr_name in row.__touched_annotations__:
                    if self.has_header:
                        letter = row.__header_back_map__[attr_name]
                    else:
                        letter = attr_name
                    new_value = getattr(row, attr_name)
                    if self.wb_values_only is not None:
                        if sheet_name not in self.wb_values_only:
                            self.wb_values_only.create_sheet(sheet_name)
                            self.wb_with_formulas.create_sheet(sheet_name)
                        elif getattr(self.wb_values_only[sheet_name][f'{letter}{recid}'], "value", None) == new_value:
                            continue
                        self.wb_values_only[sheet_name][f'{letter}{recid}'].value = new_value
                    else:
                        if sheet_name not in self.wb_with_formulas:
                            self.wb_with_formulas.create_sheet(sheet_name)
                        if self.has_header:
                            if getattr(self.wb_with_formulas[sheet_name][f'{letter}1'], "value", None) != row.__header_name_map__[attr_name]:
                                self.wb_with_formulas[sheet_name][f'{letter}1'].value = row.__header_name_map__[attr_name]

                    self.wb_with_formulas[sheet_name][f'{letter}{recid}'].value = new_value
        self.wb_with_formulas.save(out_file)

    def __str__(self):
        return f'XLSX_FILE_{hyperc.xtj.str_to_py(self.path)}'

class CSVConnector(Connector):

    def __str__(self):
        return f'CSV_FILE_{hyperc.xtj.str_to_py(self.path)}'

class GSheetConnector(XLSXConnector):

    def load(self):

        file_id = self.path
        SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.metadata','https://www.googleapis.com/auth/spreadsheets']

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('./token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())


        drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)

        # request = drive_service.files().get_media(fileId=file_id)
        request = drive_service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # request = drive_service.files().export_media(fileId=file_id, mimeType='text/csv')

        fh = io.BytesIO()

        downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

        self.path = fh
        super().load()

    def __str__(self):
        return f'GSHEET_{hyperc.xtj.str_to_py(self.path)}'

class MSAPIConnector(Connector):
    def __init__(self, path, has_header=True):
        super().__init__(self, path, has_header)
        self.ms_table = hyper_etable.ms_api.get_excel(path)
        # TODO fix code before
        # Load used cell
        for sheet in self.ms_table:
            wb_sheet=self.ms_table[sheet]
            filename = self.path
            # py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
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
            ThisTable.__connector__ = self
            self.mod.__dict__[f'{py_table_name}_Class'] = ThisTable
            self.classes[py_table_name] = ThisTable
            self.classes[py_table_name].__qualname__ = f"{self.session_name}.{py_table_name}_Class"
            self.mod.HCT_OBJECTS[py_table_name] = []
            self.objects[py_table_name]={}
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
                        raise Exception(f"We don't support table with error cell {cell}")
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
        return f'MSAPI_{hyperc.xtj.str_to_py(self.path)}'

class AirtableConnector(Connector):
    def load(self):
        BASE_ID, API_KEY, TABLE = self.path

        # response = requests.get(f'https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables?api_key={API_KEY}',).json()
        response = requests.get(f'https://api.airtable.com/v0/{BASE_ID}/{TABLE}?api_key={API_KEY}').json()
        assert 'error' not in response, f"Airtable error {response}"
        # py_table_name = hyperc.xtj.str_to_py(f'[{filename}]{sheet}')
        py_table_name = hyperc.xtj.str_to_py(f'{TABLE}') # warning only sheet in 
        ThisTable = hyper_etable.meta_table.TableElementMeta(f'{py_table_name}_Class', (object,), {'__table_name__': py_table_name, '__xl_sheet_name__': TABLE})
        ThisTable.__annotations__ = {'__table_name__': str, 'addidx': int}
        ThisTable.__user_defined_annotations__ = []
        ThisTable.__default_init__ = {}
        ThisTable.__touched_annotations__ = set()
        ThisTable.__annotations_type_set__ = collections.defaultdict(set)
        ThisTable.__connector__ = self
        self.mod.__dict__[f'{py_table_name}_Class'] = ThisTable
        self.classes[py_table_name] = ThisTable
        self.classes[py_table_name].__qualname__ = f"{self.mod.__name__}.{py_table_name}_Class"
        self.mod.HCT_OBJECTS[py_table_name] = []
        self.objects[py_table_name]={}
        ThisTable.__recid_max__ = 0
        recid = 0
        for row in response['records']:
            recid += 1
            if ThisTable.__recid_max__ < recid:
                ThisTable.__recid_max__ = recid
            rec_obj = ThisTable()
            rec_obj.addidx = -1
            rec_obj.__recid__ = recid
            rec_obj.__table_name__ += f'[{BASE_ID}]{TABLE}_{recid}'
            rec_obj.__touched_annotations__ = set()
            rec_obj.__xl_sheet_name__ = TABLE
            self.objects[py_table_name][recid] = rec_obj
            self.mod.HCT_OBJECTS[py_table_name].append(rec_obj)
            sheet_name = hyperc.xtj.str_to_py(f"{TABLE}") + f'_{recid}'
            if not hasattr(self.mod.DATA, sheet_name):
                setattr(self.mod.DATA, sheet_name, self.objects[py_table_name][recid])
                self.mod.StaticObject.__annotations__[sheet_name] = self.classes[py_table_name]
            
            rec_obj.__py_sheet_name__ = sheet_name

            for column_name, value in row['fields'].items():

                self.objects[py_table_name][recid].__touched_annotations__.add(column_name)
                if (type(value) == bool or type(value) == int or type(value) == str):
                    setattr(self.objects[py_table_name][recid], column_name, value)
                    setattr(self.objects[py_table_name][recid], column_name, value)
                    self.objects[py_table_name][recid].__class__.__annotations__[column_name] = str
                    self.objects[py_table_name][recid].__touched_annotations__.add(column_name) 
                else:
                    setattr(self.objects[py_table_name][recid], column_name, '')
                    self.objects[py_table_name][recid].__class__.__annotations__[column_name] = str
                    self.objects[py_table_name][recid].__touched_annotations__.add(column_name)
