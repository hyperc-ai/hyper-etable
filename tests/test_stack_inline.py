from hyper_etable.etable import stack_code_gen

class TAKEIF_AFORMULA_XLSX_SHEET1:
    a: str
    a_not_hasattr: bool
    b: str
    b_not_hasattr: bool
    c: str
    c_not_hasattr: bool
    def __init__(self):
        self.a = 0
        self.a_not_hasattr = True  # TODO: add this
        self.b = 0
        self.b_not_hasattr = True  # TODO: add this
        self.c = 0
        self.c_not_hasattr = True  # TODO: add this

exec(stack_code_gen("TAKEIF_AFORMULA_XLSX_SHEET1"))

def test_stack_drop():
    _stack_drop()

def test_calc():
    sheet = [ TAKEIF_AFORMULA_XLSX_SHEET1(), TAKEIF_AFORMULA_XLSX_SHEET1(), TAKEIF_AFORMULA_XLSX_SHEET1() ]
    sheet[0].a = 1
    _stack_add(sheet[0], "a")
    sheet[0].a_not_hasattr = False
    assert static_stack_sheet.row0_letter == "a"
    assert static_stack_sheet.row0_not_hasattr == False
    assert sheet[0].a_not_hasattr == False
    assert static_stack_sheet.row1_letter == ""
    assert static_stack_sheet.row1_not_hasattr == True
    assert sheet[1].a_not_hasattr == True
    _stack_drop()
    assert static_stack_sheet.row0_letter == ""
    assert static_stack_sheet.row0_not_hasattr == True 
    assert sheet[0].a_not_hasattr == True


