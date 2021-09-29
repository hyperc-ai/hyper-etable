
import hyper_etable.etable
import hyper_etable.connector
import copy

def test_mysql():
    et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    user, password, host, database, tables = "phpmyadmin", "123", "localhost", "hyperc_db", ("table1",)
    conn = hyper_etable.connector.new_connector(path=(user, password, host, database, tables), mod=et.mod,proto='mysql')
    conn.load()
    was = et.mod.HCT_OBJECTS['TABLE1'][0].column2
    et.mod.HCT_OBJECTS['TABLE1'][0].column2="changed"
    et.mod.HCT_OBJECTS['TABLE1'].append(copy.copy(et.mod.HCT_OBJECTS['TABLE1'][0]))
    et.mod.HCT_OBJECTS['TABLE1'][-1].__recid__=6
    conn.save()
    print("ok")
    et.mod.HCT_OBJECTS['TABLE1'][0].column2=was
    conn.save()


def test_mysql_dal():
    et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    user, password, host, database, tables = "phpmyadmin", "123", "localhost", "hyperc_db", ("table1",)
    conn = hyper_etable.connector.new_connector(path=(user, password, host, database, tables), mod=et.mod,proto='dal')
    conn.load()
    conn.save_raw(['table1'])
    print("ok")