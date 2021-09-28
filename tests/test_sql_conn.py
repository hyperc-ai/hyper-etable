
import hyper_etable.etable
import hyper_etable.connector

def test_mysql():
    et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    user, password, host, database, tables = "phpmyadmin", "123", "localhost", "hyperc_db", ("table1",)
    conn = hyper_etable.connector.new_connector(path=(user, password, host, database, tables), mod=et.mod,proto='mysql')
    conn.load()
    conn.save_raw(['table1'])
    print("ok")

def test_mysql2():
    pass