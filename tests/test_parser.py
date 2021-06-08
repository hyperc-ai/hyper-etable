from hyper_etable.etable_transpiler import formulas_parser

def test_parse_structref():
    formulas_parser("VLOOKUP(MINITABLE[[#THIS ROW],[MINI]], C5:D6, 2)")