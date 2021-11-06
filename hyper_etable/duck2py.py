sample = """
DEMAND#1.PRODUCT == PRODUCTS#DELIVERING.PRODUCT

# get database placeholder for this truck items
DEMAND#1.PRODUCT == TRANSPORT_CONTENTS#1.PRODUCT

# load the stuff
TRANSPORT#1.LOADED_VOLUME_IN += PRODUCTS#DELIVERING.VOLUME
TRANSPORT#1.LOADED_WEIGHT_IN += PRODUCTS#DELIVERING.WEIGHT

#get stuff from storage
STORAGE#1.PRODUCT == PRODUCTS#DELIVERING.PRODUCT
STORAGE#1.LOCATION == TRANSPORT#1.LOCATION

STORAGE#1.QUANTITY_OUT += 1
global total_loaded
total_loaded += 1
STORAGE#1.QUANTITY_OUT < 3
"""

import re


ALL_EQINEQ = ("==", "!=", "<", ">", "<=", ">=")
params_re = re.compile(r"([A-Za-z0-9_]+#[A-Za-z0-9_]+)")


def duck2py(s_duck, name):
    out = []
    all_params = {x.replace("#", "_"):x for x in params_re.findall(s_duck)}
    repl_par_map = {v: k for k, v in all_params.items()}

    fun_args = []
    for parn, duckp in all_params.items():
        clsn = duckp.split("#")[0] + "_Class"
        fun_args.append(f"{parn}: {clsn}")

    txtpars = ',\n            '.join(fun_args)
    out.append(f"def {name}(\n            {txtpars}):")

    
    for l in s_duck.split("\n"):
        if any(x in l for x in ALL_EQINEQ) and not l.strip().startswith("if"):
            l = "assert "+l
        for duckp, parn in repl_par_map.items():
            l = l.replace(duckp, parn)
        out.append("    " + l.strip())
    
    return "\n    ".join(out)
    
        
print(duck2py(sample, "test_foo"))