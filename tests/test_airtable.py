import hyper_etable.etable


def test_airtable():
    path = ['appZ5mJvdfY2ZHzzw','key3hulhtlvhMFtQ8', 'Epics']
    et = hyper_etable.etable.ETable(project_name='airtable_proiject')
    et.open_from(path=path, proto='airtable')
    print("ok")
