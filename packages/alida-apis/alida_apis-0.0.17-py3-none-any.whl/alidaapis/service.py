import requests
import json
from .auth import _get_token
from .utils import read_var


def get(order = "id", desc="true", limit=20, page=1):
    url = read_var("url_base") + read_var("url_services") + "?sort=" + order + "&desc=" + desc + "&size=" + str(limit) + "&page=" + str(page)

    payload = {}
    headers = {
        'authorization': 'Bearer ' + _get_token()
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)

def get_services_by_name(name):
    result = []
    services = get()['content']
    
    for service in services:
        if service['name'] == name:
            result.append(service)
    return result

def get_by_id(id):
    url = read_var("URL_ADD_SERVICES") + "/" + str(id)
    payload = {}
    headers = {
        'authorization': 'Bearer ' + _get_token()
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)


def add(service_metamodel, auto_update_version=False):
    
    if auto_update_version:
        name = service_metamodel['name']
        version = service_metamodel['version']
        if len(get_services_by_name(name))>0:
            latest = get_services_by_name(name)[0]
            vers = latest['version'].split(".")
            vers[-1] = str(int(vers[-1]) + 1)
            version = ".".join(vers)
            service_metamodel['version'] = version

    
    url = read_var("url_add_services")

    payload = service_metamodel
    headers = {
        'authorization': 'Bearer ' + _get_token(),
        'content-type': 'application/json'
    }
    return requests.request("POST", url, headers=headers, data=json.dumps(payload))
