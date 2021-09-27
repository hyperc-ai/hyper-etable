import hyper_etable.etable
import uuid
import requests_oauthlib
import threading
import webbrowser
import flask
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
session_state = str(uuid.uuid4())
client_id='560227148876-h8o4hcttgo75ig2tcn3qgjrc73c13mkc.apps.googleusercontent.com'
client_secret = "wr8sP8MTNSFw65-gQfhlSCIz"
redirect_uri = 'http://localhost:5000/getToken'
scope = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.metadata','https://www.googleapis.com/auth/spreadsheets']
oauth = requests_oauthlib.OAuth2Session(client_id, redirect_uri=redirect_uri,
                        scope=scope)
authorization_url, state = oauth.authorization_url(
    'https://accounts.google.com/o/oauth2/auth',
    # access_type and prompt are Google specific extra
    # parameters.
    access_type="offline", prompt="select_account")
def web_server():
    web_server_app = flask.Flask(f'{__name__}-{session_state}')

    @web_server_app.route('/getToken')  # Its absolute URL must match your app's redirect_uri set in AAD
    def authorized():
        print(f"code is {flask.request.args.get('code')}")
        # if flask.request.args.get('code'):
        #     if "error" in result:
        #         raise RuntimeError(f'auth_error {result}')

        try:
            token = oauth.fetch_token(

                # 'https://accounts.google.com/o/oauth2/auth'
            'https://accounts.google.com/o/oauth2/token',
    # "https://oauth2.googleapis.com/token",
            code=flask.request.args.get('code'),
            # Google specific extra parameter used for client
            # authentication
            client_secret=client_secret)
        except Exception as a:
            print(a)
          
        return "Please close tab"

    try:
        web_server_app.run(port=5000)
    except RuntimeError as msg:
        print("Exit autoriser")
        if str(msg) == "Server going down":
            pass  # or whatever you want to do when the server goes down
        else:
            pass

def test_gsheet():
    # file_id = '1IGqkZK3yOvejLFBSjTPxrwSkJDZLjX-ibnGjAq6SAps'
    # et = hyper_etable.etable.ETable(project_name='test_custom_class_edited')
    # gconn=et.open_from(path=file_id, has_header=False, proto='gsheet')
    # gconn.save()
    # path = ['appZ5mJvdfY2ZHzzw','key3hulhtlvhMFtQ8', 'Epics']
    # et.open_from(path=path, proto='airtable')
    # print("ok")



    print(state)
    thread = threading.Thread(target=web_server)
    thread.start()
    webbrowser.open(authorization_url, new=2)
    thread.join()
