"""
CREATE OR REPLACE PROCEDURE public.hyperc_transit(IN sql_command character varying)
    LANGUAGE 'plpython3u'
AS $BODY$
"""

import logzero 
from logzero import logger 
# from typing import Any, TYPE_CHECKING

# if TYPE_CHECKING:
#     plpy: Any = {}
#     sql_command: Any = {}


import hyperc
from collections import defaultdict
import hyper_etable.etable
from itertools import combinations
logzero.logfile("/tmp/plhyperc.log")
input_py = '/tmp/actions.py'

SQL_PROCEDURES = """
select n.nspname as function_schema,
    p.proname as function_name,
    p.prosrc as source,
    l.lanname as function_language,
    pg_get_function_arguments(p.oid) as function_arguments,
    t.typname as return_type
from pg_proc p
left join pg_namespace n on p.pronamespace = n.oid
left join pg_language l on p.prolang = l.oid
left join pg_type t on t.oid = p.prorettype 
where n.nspname not in ('pg_catalog', 'information_schema') and l.lanname = 'hyperc' and t.typname = 'void'
order by function_schema,
         function_name;
"""

SQL_GET_PRIMARYKEYS = """
SELECT c.column_name, c.data_type
FROM information_schema.table_constraints tc 
JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name) 
JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
  AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
WHERE constraint_type = 'PRIMARY KEY' and tc.table_name = '{table_name}';
"""

SQL_GET_ALLCOLUMNS = """
SELECT
    column_name,
    data_type
FROM
    information_schema.columns
WHERE
    table_name = '{table_name}';
"""

logger.debug(sql_command)  
 
sql_command_l = sql_command
supported_commands = ["INSERT", "UPDATE"]

if not any(x in sql_command_l.upper() for x in supported_commands):
    raise NotImplementedError("Only INSERT and UPDATE are supported")

if "WITH" in sql_command_l:
    raise NotImplementedError("WITH statement not supported")


autotransit_commands = ["TRANSIT UPDATE", "TRANSIT INSERT", "TRANSIT TO"]

goal_func = ""
exec_sql = ""

all_executed_commands = []
tables_names = [] 

if any(x in sql_command_l.upper() for x in autotransit_commands):
    txid1 = plpy.execute("SELECT txid_current();")[0]["txid_current"]
    txid2 = plpy.execute("SELECT txid_current();")[0]["txid_current"]
    if txid1 != txid2:
        plpy.error("Can not TRANSIT in autotransit mode inside an open transaction")
    
    if "TRANSIT TO" in sql_command_l.upper():
        goal_func = sql_command_l.lower().split("transit to")[1].strip().split()[0]
        table_names = [x.strip() for x in sql_command_l.lower().split(" from ")[1].split(",")]
    elif "TRANSIT UPDATE" in sql_command_l.upper():
        tables_names = [ sql_command_l.lower().split("transit update")[1].split()[0] ]
        exec_sql = sql_command_l.replace("TRANSIT UPDATE", "UPDATE")
        exec_sql = exec_sql.replace("TRANSIT UPDATE".lower(), "UPDATE")
    elif "TRANSIT INSERT INTO" in sql_command_l.upper():
        tables_names = [ sql_command_l.lower().split("transit insert into")[1].split()[0] ]
        exec_sql = sql_command_l.replace("TRANSIT INSERT INTO", "INSERT INTO")
        exec_sql = exec_sql.replace("TRANSIT INSERT INTO".lower(), "INSERT INTO")
    else:
        raise RuntimeError("Wrong TRANSIT parse")

    # plpy.execute("BEGIN;")
    # plpy.execute("SAVEPOINT hyperc_sp1;")
    if exec_sql:
        logger.debug(f"Executing {exec_sql}")
        plpy.execute(exec_sql)
        all_executed_commands.append(exec_sql)
else:
    plpy.error("TRANSIT to end a transaction is not yet implemented")

all_tables_names = [x["table_name"] for x in plpy.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'public';")]


EQ_CMP_OPS = [" == ", " != ", " < ", " > ", " <= ", " >= "]

sources_list = []
for src in plpy.execute(SQL_PROCEDURES):
    args = ", ".join([f"{argpair.strip().split()[0]}: {argpair.strip().split()[1].upper()}_Class" for argpair in src['function_arguments'].split(",")])
    tables_names.extend([f"{argpair.strip().split()[1]}" for argpair in src['function_arguments'].split(",")])
    fun_src = f"""def {src['function_name']}({args}):"""
    for src_line in src["source"].split("\n"):
        fun_src += "    "+src_line+"\n"
    if src['function_name'] == goal_func:
        fun_src += "    DATA.GOAL = True\n"
    sources_list.append(fun_src)

stub_hashed_commands = " ".join(all_executed_commands)

if not goal_func:
    fun_argcount = defaultdict(lambda: 0)
    fun_args = []
    goal_fun_src = []
    # Now generate goal
    for tbl in all_tables_names:
        logger.debug(f"Scanning for change {tbl}")
        updates = plpy.execute(f"SELECT * FROM {tbl} WHERE xmin::text = ((txid_current()+1) % (2^32)::bigint)::text;")
        txid_current = plpy.execute(f"SELECT txid_current();")
        logger.debug(f"Seeing updates for {tbl}: {updates} with {txid_current}")
        local_varnames = []
        for updated_row in updates:
            logger.debug(f"Scanning for change {tbl} row {updated_row}")
            varname = f"selected_{tbl}_{fun_argcount[tbl]}"
            local_varnames.append(varname)
            fun_argcount[tbl] += 1
            fun_args.append(f"{varname}: {tbl.upper()}_Class")
            for k, v in dict(updated_row).items():
                if k.upper() not in stub_hashed_commands.upper():
                    continue
                logger.debug(f"Scanning for change {tbl} row {updated_row} item {k}, {v}")
                goal_fun_src.append(f"assert {varname}.{k.upper()} == {repr(v)}")
            for ineq_pair in combinations(local_varnames, 2):
                goal_fun_src.append(f"assert {ineq_pair[0]} != {ineq_pair[1]}")
    if len(goal_fun_src) > 0:
        goal_fun_name = "goal_from_transaction_updates"
        s_fun_args = ", ".join(fun_args)
        goal_func_code = f"def {goal_fun_name}({s_fun_args}):\n    " + "\n    ".join(goal_fun_src)
        goal_func_code += "\n    DATA.GOAL = True\n"

        sources_list.append(goal_func_code)
        assert exec_sql, "Must have UPDATE or INSERT executed"
        plpy.rollback()
    else:
        plpy.error("No transition defined.")


source = "\n".join(sources_list)
logger.debug(f"Actions:\n {source}")

with open(input_py, 'w') as file:
    file.write(source)

base = {}
for t_n in tables_names:
    base[t_n] = dict(enumerate(list(plpy.execute(f"SELECT * FROM {t_n}", 1000))))
    logger.debug(base[t_n])

et = hyper_etable.etable.ETable(project_name='test_connnection_trucks')
db_connector = et.open_from(path=base, has_header=True, proto='raw', addition_python_files=[input_py])
et.dump_py(out_filename='/tmp/classes.py')
et.solver_call_plan_n_exec()
tables = db_connector.get_update()
logger.debug(f"Update: {tables}")
for tablename, rows in tables.items():
    if len(rows) == 0:
        continue
    pks = {x["column_name"]:x["data_type"] for x in plpy.execute(SQL_GET_PRIMARYKEYS.format(table_name=tablename))}
    all_columns = {x["column_name"]:x["data_type"] for x in plpy.execute(SQL_GET_ALLCOLUMNS.format(table_name=tablename))}
    for _, row in rows.items():
        update_where_q = []
        update_set_q = []
        for colname, val in row.items():
            if colname in pks:
                update_where_q.append(f"{colname} = {repr(val)}")
            else:
                if type(val) == str and not "char" in all_columns[colname] and not "text" in all_columns[colname] and len(val) == 0:
                    logger.warning(f"Skipping update of unsupported type {all_columns[colname]} for {tablename}.{colname} with value {repr(val)}")
                    continue
                update_set_q.append(f"{colname} = {repr(val)}")
        if len(update_set_q) == 0: 
            logger.warning(f"Skipping empty update for {tablename}: {row}")
            continue  # should never happen!
        if len(update_where_q) == 0: 
            logger.warning(f"Skipping update for table without primary key {tablename}: {row}")
            continue 
        set_subq = ", ".join(update_set_q)
        where_subq = " AND ".join(update_where_q)
        query = f'UPDATE {tablename} SET {set_subq} WHERE {where_subq};'
        logger.debug(f"Executing, {query}")
        plpy.execute(query)
    

tables = db_connector.get_append()
logger.debug(f"Append: {tables}")
for tablename, rows in tables.items():
    if len(rows) == 0:
        continue
    for _, row in rows.items():
        val = ", ".join([f'\'{repr(val)}\'' for _, val in row.items()])
        col_name = ", ".join([f'"{col}"' for col, _ in row.items()])
        query = f"INSERT INTO {tablename} ({col_name}) VALUES ({val});"
        logger.debug(f"Executing, {query}")
        plpy.execute(query)

""" 
$BODY$;
"""