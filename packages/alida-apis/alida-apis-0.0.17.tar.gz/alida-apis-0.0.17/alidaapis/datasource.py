from .utils import read_var
from .auth import _get_token
import requests, json

def get_all():
    
    url = read_var("url_base") + read_var("url_datasources")
    
    payload = {}
    headers = {
        'authorization': 'Bearer ' + _get_token(),
    }

    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)

def get_by_id(id):
    datasources = get_all()
    for datasource in datasources:
        if int(datasource['id']) == int(id):
            return datasource


def get_by_name(name):
    datasources = get_all()
    for datasource in datasources:
        if datasource['name'] == name:
            return datasource
