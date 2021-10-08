# def solve():
try:
    import sys
    import hyper_etable.etable
    import io
    limit = 1000
    tables_names = ['transport', 'location']
    input_py = '/tmp/actions.py'
    with open('/tmp/plpython.out', 'a') as f:
        print(sys.version, file=f)
        base = {}
        for t_n in tables_names:
            base[t_n] = dict(enumerate(list(plpy.execute(f"SELECT * FROM {t_n}", limit))))
            print(base[t_n], file=f)
        print('enf', file=f)
        # todo save all sources here
        source = plpy.execute(
            "SELECT routine_definition FROM information_schema.routines WHERE specific_schema LIKE 'public';")
        source = source[0]['routine_definition']
        print("Source code:")
        print(source, file=f)
        with open(input_py, 'w') as file:
            file.write(source)
        et = hyper_etable.etable.ETable(project_name='test_connnection_trucks')
        db_connector = et.open_from(path=base, has_header=True, proto='raw', addition_python_files=[input_py])
        et.dump_py(out_filename='/tmp/classes.py')
        et.solver_call_plan_n_exec()
        tables = db_connector.get_update()
        print("Update:", file=f)
        print(tables, file=f)
        for table in tables:
            if len(tables[table]) == 0:
                continue
            # TODO read column name here
            # columns = inspector.get_columns(table)
            recid_column_name = 'id'  # list(columns)[0]['name']
            for _, row in tables[table].items():
                recid = row['id']
                set_column = ", ".join([f'"{col}" = \'{val}\'' for col, val in row.items()])
                query = f'UPDATE {table} SET {set_column} WHERE "{recid_column_name}" = {recid}'
                print(query, file=f)
                plpy.execute(query, limit)
        tables = db_connector.get_append()
        print("Append:", file=f)
        print(tables, file=f)
        for table in tables:
            if len(tables[table]) == 0:
                continue
            # TODO read column name here
            # columns = inspector.get_columns(table)
            recid_column_name = 'id'  # list(columns)[0]['name']
            for _, row in tables[table].items():
                recid = row['id']
                val = ", ".join([f'\'{val}\'' for _, val in row.items()])
                col_name = ", ".join([f'"{col}"' for col, _ in row.items()])
                query = f"INSERT INTO {table}(\"{recid_column_name}\", {col_name}) VALUES ('{recid}', {val})"
                plpy.execute(query, limit)
    return True
except:
    import traceback
    plpy.error(traceback.format_exc())
