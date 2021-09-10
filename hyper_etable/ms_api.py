import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
import msal
import hyper_etable.ms_app_config
import json
import os
import webbrowser
import urllib.parse as urlparse
from urllib.parse import parse_qs
import threading
from gspread.models import Cell
import itertools
import time

ms_session = {"state": "", "user": ""}
# Start MS API
run_ms_app_lock = threading.Lock()
run_ms_app_lock.acquire(0)

MICROSOFT_AUTHORIZED_USER_FILENAME = 'authorized_user_ms.json'

def sing_out():
    try:
        os.remove(MICROSOFT_AUTHORIZED_USER_FILENAME)
    except FileNotFoundError:
        pass

# def run_ms_app():
#     ms_app = Flask(f'{__name__}-{ms_session["state"]}')
#     #ms_app.config.from_object(hyper_etable.ms_app_config)

#     # a simple page that says hello
#    # ms_app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # @ms_app.route('/getAToken')  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    # if request.args.get('state') != ms_session.get("state"):
    #     logger.info(f"{request.args.get('state')} != {ms_session.get('state')}")
    #     raise RuntimeError(f"{request.args.get('state')} != {ms_session.get('state')}")
    # if "error" in request.args:  # Authentication/Authorization failure
    #     return render_template("auth_error.html", result=request.args)
    print(f"code is {request.args.get('code')}")
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=hyper_etable.ms_app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for("authorized", _external=True))
        if "error" in result:
            raise RuntimeError(f'auth_error {result}')
        ms_session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    run_ms_app_lock.release()
    return "Please close tab"

    # try:
    #     ms_app.run(port=5001)
    # except RuntimeError as msg:
    #     print("Exit autoriser")
    #     if str(msg) == "Server going down":
    #         pass  # or whatever you want to do when the server goes down
    #     else:
    #         pass


def ms_login():
    ms_session["state"] = str(uuid.uuid4())
    # thread = threading.Thread(target=run_ms_app)
    # thread.start()
    webbrowser.open(_build_auth_url(scopes=hyper_etable.ms_app_config.SCOPE, state=ms_session["state"]), new=2)
    run_ms_app_lock.acquire()
    time.sleep(1)
    # thread.abort()
    run_ms_app_lock.release()

#https://graph.microsoft.com/v1.0/me/drive/items/CFE36FE507A85213!105/workbook/createSession
#https://graph.microsoft.com/v1.0/me/drive/items/CFE36FE507A85213!105/workbook/worksheets('Sheet1')/usedRange

def prepare_excel(shs):
    token = _get_token_from_cache(hyper_etable.ms_app_config.SCOPE)
    if not token:
        ms_login()
        token = _get_token_from_cache(hyper_etable.ms_app_config.SCOPE)

    parsed = urlparse.urlparse(shs)
    args = urlparse.parse_qs(parsed.query)
    sheets = {}
    document_id = args['resid'][0]

    print("url ", shs)

    response = requests.get(
        f'https://graph.microsoft.com/v1.0/me/drive/items/{document_id}/workbook/worksheets',
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()

    print(response)

    if response.get('error'):
        raise RuntimeError(f"{response['error']['message']}")

    if args.get('activeCell'):
        sheet = args['activeCell'][0].split('!')[0]
        print("sheet is ", sheet)
        sheet = ''.join(c for c in sheet if c not in '\'"')
        try:
            sheet_position = int(sheet)
        except:
            sheet_position = -1
        for x in response['value']:
            print(f"{x['name']} == {sheet} {x['name'] == sheet} ")
            if x['name'] == sheet or x['position'] == sheet_position or x['id'] == sheet:
                sheets[x['id']] = x['name']
                print("select ", x['name'])
                break
    else:
        for x in response['value']:
            sheets[x['id']] = (x['name'])

    print(f'prepare {sheets}')

    return (document_id, sheets, token)

#full comatibility
def get_digit_index_from_excel(excel_index):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    #get char index size
    char_index_size = 0
    for c in excel_index:
        if c in alphabet:
            char_index_size += 1
    char_index = excel_index[0:char_index_size]
    digit_index = 0
    counter = 0
    for c in reversed(char_index):
        digit_index = digit_index + alphabet.index(c) * (len(alphabet) ** counter)
        counter += 1
    return (digit_index, int(excel_index[char_index_size:])-1)


def get_excel(shs):
    document_id, sheet_ids, token = prepare_excel(shs)

    sheets = {}
    json_request = {"requests": []}
    counter = 0
    for sheet_id in sheet_ids:
        json_request['requests'].append({
            "id": counter,
            "method": "GET",
            "url": f"/me/drive/items/{document_id}/workbook/worksheets/{sheet_ids[sheet_id]}/usedRange(valuesOnly=true)"})
        counter += 1
    print(json_request)
    print("!!!!!!!!!!!!!")
    responses = requests.post(url='https://graph.microsoft.com/v1.0/$batch',
        json=json_request, headers={'Authorization': 'Bearer ' + token['access_token']}).json()

    print(responses)
    if responses.get('error'):
        raise RuntimeError(f"{responses['error']['message']}")
    for x in responses['responses']:
        sheet_name = x['body']['address'].split('!')[0]
        start_col, start_row = get_digit_index_from_excel(x['body']['address'].split('!')[1].split(':')[0])
        if len(x['body']['address'].split('!')[1].split(':')) > 1:
            stop_col, stop_row = get_digit_index_from_excel(x['body']['address'].split('!')[1].split(':')[1])

        print(x['body']['address'].split('!')[1].split(':')[0], "->", start_col, start_row)
        if start_col > 0:
            row_prepend = []
            sheets[sheet_name] = []
            for i in range(start_col):
                row_prepend.append("")
            for row in x['body']['values']:
                sheets[sheet_name].append(list(itertools.chain(row_prepend, row)))
        else:
            sheets[sheet_name] = x['body']['values']
        if start_row > 0:
            matrix = []
            for i in range(start_row):
                row = []
                matrix.append(row)
                for j in range(stop_col+1):
                    row.append("")
            sheets[sheet_name] = list(itertools.chain(matrix, sheets[sheet_name]))
    return sheets

def put_excel(shs, table):
    document_id, sheet, token = prepare_excel(shs)
    json = {
        "values": table, 
    }
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    charIndex = alphabet[len(table[0])-1]
    # if len(table[0]) > len(alphabet):
    #     charIndex = alphabet[len(alphabet)/len(table[0])] + alphabet[len(alphabet)%len(table[0])]

    range = 'A1:' + charIndex + str(len(table))
    # print(json)
    # print(range)
    response = requests.patch(f"https://graph.microsoft.com/v1.0/me/drive/items/{document_id}/workbook/worksheets/{sheet}/range(address='{range}')",
        json=json, headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    # print('patch response ', response)

def _load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(MICROSOFT_AUTHORIZED_USER_FILENAME):
        with open(MICROSOFT_AUTHORIZED_USER_FILENAME) as json_file:
            try:
                data = json.load(json_file)
                if 'refresh_token' in data:
                    cache.deserialize(data['refresh_token'])
            except json.decoder.JSONDecodeError:
                pass
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        with open(MICROSOFT_AUTHORIZED_USER_FILENAME, 'w+') as json_file:
            try:
                data = json.load(json_file)
            except json.decoder.JSONDecodeError:
                data = {}
            data['refresh_token'] = cache.serialize()
            json_file.seek(0)
            json.dump(data, json_file)
            json_file.truncate()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        hyper_etable.ms_app_config.CLIENT_ID, authority=authority or hyper_etable.ms_app_config.AUTHORITY,
        client_credential=hyper_etable.ms_app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri="http://localhost:5000/getAToken")


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

class MSSheet:

    def __init__(self, url, table=None):
        self.url = url
        self.table = table
        if self.table is None:
            self.table = []
        self.row_amount = len(self.table)
        if self.row_amount == 0:
            self.col_amount = 0
        else:
            self.col_amount = len(self.table[0])

    def update_cells(self, cells: [Cell]):
        col_amount_was = self.col_amount
        for cell in cells:
            if self.row_amount < cell.row:
                self.row_amount = cell.row
            if self.col_amount < cell.col:
                self.col_amount = cell.col
        #resize table to fit
        if len(self.table) != self.row_amount:
            for i in range(self.row_amount - len(self.table)):
                self.table.append([])
        if col_amount_was != self.col_amount:
            for row in self.table:
                if len(row) < self.col_amount:
                    for i in range(self.col_amount - len(row)):
                        row.append("")

        #fill resized table with
        for cell in cells:
            self.table[cell.row-1][cell.col-1] = cell.value

        put_excel(self.url,self.table)
