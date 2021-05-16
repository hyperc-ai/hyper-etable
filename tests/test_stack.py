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


class StaticStackSheet:
    row0: TAKEIF_AFORMULA_XLSX_SHEET1
    row0_letter: str
    row0_not_hasattr: bool
    row1: TAKEIF_AFORMULA_XLSX_SHEET1
    row1_letter: str
    row1_not_hasattr: bool
    row2: TAKEIF_AFORMULA_XLSX_SHEET1
    row2_letter: str
    row2_not_hasattr: bool
    row3: TAKEIF_AFORMULA_XLSX_SHEET1
    row3_letter: str
    row3_not_hasattr: bool
    row4: TAKEIF_AFORMULA_XLSX_SHEET1
    row4_letter: str
    row4_not_hasattr: bool

    def __init__(self):
        self.row0_not_hasattr = True
        self.row1_not_hasattr = True
        self.row2_not_hasattr = True
        self.row3_not_hasattr = True
        self.row4_not_hasattr = True
        self.row0_letter = ""
        self.row1_letter = ""
        self.row2_letter = ""
        self.row3_letter = ""
        self.row4_letter = ""
        

static_stack_sheet = StaticStackSheet()


#@not_planned
def _drop_letter(obj, letter):
    if letter == "a":
        obj.a_not_hasattr = True
    elif letter == "b":
        obj.b_not_hasattr = True
    elif letter == "c":
        obj.c_not_hasattr = True


def stack_add(obj: TAKEIF_AFORMULA_XLSX_SHEET1, letter: str):
    if static_stack_sheet.row0_not_hasattr == True:
        static_stack_sheet.row0 = obj
        static_stack_sheet.row0_letter = letter
        static_stack_sheet.row0_not_hasattr = False
    elif static_stack_sheet.row1_not_hasattr == True:
        static_stack_sheet.row1 = obj
        static_stack_sheet.row1_letter = letter
        static_stack_sheet.row1_not_hasattr = False
    elif static_stack_sheet.row2_not_hasattr == True:
        static_stack_sheet.row2 = obj
        static_stack_sheet.row2_letter = letter
        static_stack_sheet.row2_not_hasattr = False
    elif static_stack_sheet.row3_not_hasattr == True:
        static_stack_sheet.row3 = obj
        static_stack_sheet.row3_letter = letter
        static_stack_sheet.row3_not_hasattr = False
    elif static_stack_sheet.row4_not_hasattr == True:
        static_stack_sheet.row4 = obj
        static_stack_sheet.row4_letter = letter
        static_stack_sheet.row4_not_hasattr = False

def stack_drop():
    static_stack_sheet.row0_not_hasattr = True
    static_stack_sheet.row1_not_hasattr = True
    static_stack_sheet.row2_not_hasattr = True
    static_stack_sheet.row3_not_hasattr = True
    static_stack_sheet.row4_not_hasattr = True
    if static_stack_sheet.row0_letter != "":
        _drop_letter(static_stack_sheet.row0, static_stack_sheet.row0_letter)
        static_stack_sheet.row0_letter = ""
    if static_stack_sheet.row1_letter != "":
        _drop_letter(static_stack_sheet.row1, static_stack_sheet.row1_letter)
        static_stack_sheet.row1_letter = ""
    if static_stack_sheet.row2_letter != "":
        _drop_letter(static_stack_sheet.row2, static_stack_sheet.row2_letter)
        static_stack_sheet.row2_letter = ""
    if static_stack_sheet.row3_letter != "":
        _drop_letter(static_stack_sheet.row3, static_stack_sheet.row3_letter)
        static_stack_sheet.row3_letter = ""
    if static_stack_sheet.row4_letter != "":
        _drop_letter(static_stack_sheet.row4, static_stack_sheet.row4_letter)
        static_stack_sheet.row4_letter = ""


def test_stack_drop():
    stack_drop()

def test_calc():
    sheet = [ TAKEIF_AFORMULA_XLSX_SHEET1(), TAKEIF_AFORMULA_XLSX_SHEET1(), TAKEIF_AFORMULA_XLSX_SHEET1() ]
    sheet[0].a = 1
    stack_add(sheet[0], "a")
    sheet[0].a_not_hasattr = False
    assert static_stack_sheet.row0_letter == "a"
    assert static_stack_sheet.row0_not_hasattr == False
    assert sheet[0].a_not_hasattr == False
    assert static_stack_sheet.row1_letter == ""
    assert static_stack_sheet.row1_not_hasattr == True
    assert sheet[1].a_not_hasattr == True
    stack_drop()
    assert static_stack_sheet.row0_letter == ""
    assert static_stack_sheet.row0_not_hasattr == True 
    assert sheet[0].a_not_hasattr == True


