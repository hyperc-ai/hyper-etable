
import hyperc.xtj

class Connector:
    def __init__(self, path):
        self.path = path


class XLSXConnector(Connector):

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

