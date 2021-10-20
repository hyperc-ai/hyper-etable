
import hyper_etable.etable
import hyper_etable.connector
import copy
import shutil
import os

def test_mysql():
    et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    user, password, host, database, tables = "phpmyadmin", "123", "localhost", "hyperc_db", ("table1",)
    conn = hyper_etable.connector.new_connector(path=(user, password, host, database, tables), mod=et.mod,proto='mysql')
    conn.load()
    was = et.mod.HCT_OBJECTS['TABLE1'][0].column2
    et.mod.HCT_OBJECTS['TABLE1'][0].column2="changed"
    end_recid = et.mod.HCT_OBJECTS['TABLE1'][-1].__recid__
    et.mod.HCT_OBJECTS['TABLE1'].append(copy.copy(et.mod.HCT_OBJECTS['TABLE1'][0]))
    et.mod.HCT_OBJECTS['TABLE1'][-1].__recid__= end_recid+1
    conn.save()
    print("ok")



def test_mysql_sqlalchemy():
    et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    path = ("mysql+pymysql://phpmyadmin:123@localhost/hyperc_db", ('table1',))
    conn = hyper_etable.connector.new_connector(path=path, mod=et.mod,proto='sqlalchemy')
    conn.load()
    et.mod.HCT_OBJECTS['TABLE1'][0].column2="sqlalchemy_changed2"
    end_recid = et.mod.HCT_OBJECTS['TABLE1'][-1].__recid__
    et.mod.HCT_OBJECTS['TABLE1'].append(copy.copy(et.mod.HCT_OBJECTS['TABLE1'][0]))
    et.mod.HCT_OBJECTS['TABLE1'][-1].__recid__= end_recid+1
    conn.save()
    print("ok")


def test_con_trucks():
    input_py_filename='./tests/trucks_db/trucks.py'
    output_xlsx_filename='./tests/trucks_db/trucks_output.xlsx'
    try:
        os.remove('/home/andrey/sandbox/ch/hyper-etable/tests/trucks_db/trucks_copy.db')
    except FileNotFoundError: 
        pass
    shutil.copy('/home/andrey/sandbox/ch/hyper-etable/tests/trucks_db/trucks.db',
                '/home/andrey/sandbox/ch/hyper-etable/tests/trucks_db/trucks_copy.db')
    input_db = (
        'sqlite://///home/andrey/sandbox/ch/hyper-etable/tests/trucks_db/trucks_copy.db',
        ('Transport', 'Location Adjacency'))
    output_classes_filename='./tests/trucks_db/trucks_class.py'
    output_plan_file = './tests/trucks_db/trucks_plan.py'
    et = hyper_etable.etable.ETable(project_name='test_connnection_trucks')
    db_connector = et.open_from(path=input_db, has_header=True, proto='sqlalchemy', addition_python_files=[input_py_filename])
    et.dump_py(out_filename=output_classes_filename) # save classes in py file
    et.solver_call_plan_n_exec() # solve with execution in pddl.py
    et.save_plan(prefix='et.mod.DATA.', out_filename=output_plan_file) # save execution plan in py file

    # db_connector.save()

    # save all data to file
    xlsx_connector = hyper_etable.connector.XLSXConnector(path=output_xlsx_filename, mod=et.mod, has_header=True)
    xlsx_connector.save_all()


def test_raw_base():

    base = {}
    base['table1'] ={}
    base['table1'][1]={}
    base['table1'][1]['col1']='name1'
    base['table1'][1]['col2'] = 'name2'
    base['table1'][2] = {}
    base['table1'][2]['col1'] = 'name222'
    base['table1'][2]['col2'] = 'name2222'
    et = hyper_etable.etable.ETable(project_name='test_connnection_trucks')
    db_connector = et.open_from(path=base, has_header=True, proto='raw', addition_python_files=[])
    db_connector.load()
    et.mod.HCT_OBJECTS['TABLE1'][0].COL1 = 'nnnnn'
    # et.mod.HCT_OBJECTS['TABLE1'][0].__class__()
    # et.mod.HCT_OBJECTS['TABLE1'][1].COL1 = 'gggg'
    # et.mod.HCT_OBJECTS['TABLE1'][1].__recid__ = 5
    a = db_connector.get_append()
    u = db_connector.get_update()
    print(a)
    print(u)


