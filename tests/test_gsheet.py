import hyper_etable.etable


def test_gsheet():
    file_id = '1IGqkZK3yOvejLFBSjTPxrwSkJDZLjX-ibnGjAq6SAps'
    et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    et.open_from(path=file_id, has_header=True, proto='gsheet')
    et.open_from(path=file_id, has_header=True, proto='gsheet')
    et.open_from(path=file_id, has_header=True, proto='gsheet')
    print("ok")
