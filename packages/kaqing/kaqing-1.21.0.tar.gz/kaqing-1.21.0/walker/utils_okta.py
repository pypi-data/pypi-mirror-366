import json
from oktaloginwrapper import OktaLoginWrapper as OLW
import requests

def apps(okta: str, username: str, password: str):
    my_session = OLW.OktaSession(okta)
    my_session.okta_auth(username=username, password=password)
    my_apps = my_session.app_list()

    for app in my_apps:
        url = app.get('linkUrl')
        try:
            my_app = my_session.connect_to(url)
            print(url, True)
        except Exception as e:
            print(url, e)

def login(okta: str, username: str, password: str):
    session = OLW.OktaSession(okta)
    session.okta_auth(username=username, password=password)
    apps = session.app_list()
    # print(json.dumps(apps))

    session.connect_to('https://stgawsscpsr.c3.ai/c3/c3/static')
    print('SEAN connected')

    # for app in apps:
    #     url = app.get('linkUrl')
    #     label = app.get('label')
    #     try:
    #         my_app: requests.models.Response = session.connect_to(url)
    #         print(url, my_app.url, label, True)
    #     except Exception as e:
    #         print(url, label, False)

    return session.okta_session

def login2(okta: str, username: str, password: str):
    # https://stgawsscpsr.c3.ai/c3/c3/static/console/index.html
    r: requests.Response = requests.get('https://stgawsscpsr.c3.ai/c3/c3/static/console/index.html')