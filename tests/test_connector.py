import hyper_etable.etable


def test_gsheet():
    file_id = '1IGqkZK3yOvejLFBSjTPxrwSkJDZLjX-ibnGjAq6SAps'
    et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    gconn=et.open_from(path=file_id, has_header=False, proto='gsheet')
    gconn.save()
    # path = ['appZ5mJvdfY2ZHzzw','key3hulhtlvhMFtQ8', 'Epics']
    # et.open_from(path=path, proto='airtable')
    # print("ok")
