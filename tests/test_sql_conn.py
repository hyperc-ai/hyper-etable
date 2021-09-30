
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