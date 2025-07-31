from .utils import read_var
from .auth import _get_token
import requests, json
import datetime
import time


def start(bda_id):
    url = read_var("url_base") + read_var("url_apps") + "/" + bda_id + "/start/" + str(int(bda_id)+1)
    
    payload = json.dumps({})
    headers = {
    'authorization': 'Bearer ' + _get_token(),
    'content-type': 'application/json'
    }

    return requests.request("POST", url, headers=headers, data=payload)

def get_info(bda_id):

    url = read_var('URL_BASE') + read_var('URL_APPS') +"/" + bda_id

    payload = json.dumps({})
    headers = {
    'authorization': 'Bearer ' + _get_token(),
    'content-type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)

def latest_run_status(bda_id):
    info = get_info(bda_id)
    
    dateOfLastStatus = datetime.datetime.strptime("2000-01-01T00:00:00", '%Y-%m-%dT%H:%M:%S')

    for element in info['workflows']:
        for run in element['runs']:
            curr_date = datetime.datetime.strptime(run['dateOfLastStatus'][:-10], '%Y-%m-%dT%H:%M:%S')
            if curr_date>dateOfLastStatus:
                dateOfLastStatus = curr_date
                id = run['k8sRunId']
                
    for element in info['workflows']:
        for run in element['runs']:
            if run['k8sRunId'] == id:
                return run['currentStatus']

def synchronous_wait_till_ends(bda_id, timeout = 60):
    time.sleep(4) # Remove this with a better way of checking that the app is running first
    start = time.time()
    # Wait while BDA is running or until the defined timeout
    while latest_run_status(bda_id=bda_id) == "RUNNING":
        time.sleep(10)
        print("App is running, wait...")
        if time.time() - start > int(timeout):
            break

def start_with_parameters(params, bda_id, wf_id = None):

    if wf_id is None:
        wf_id = str(int(bda_id)+1)

    url = read_var('URL_BASE') + read_var('URL_APPS') + "/" + bda_id + "/start/" + wf_id
    print(bda_id, wf_id)
    print(url)
    payload = json.dumps({
        "services": params
    })
    
    headers = {
        'authorization': 'Bearer ' + _get_token(),
        'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
        
    return response 


def get_all(order="id"):

    payload = {}
    headers = {
        'authorization': 'Bearer ' + _get_token(),
    }

    response = requests.request("GET", url = read_var('URL_BASE') + read_var('URL_APPS') + "?order="+order, headers=headers, data=payload)

    return response

def get_by_name(name):
    bdas = []
    response = get_all()

    for element in json.loads(response.text)['collection']:
        if element['name'].lower()==name.lower():
            bdas.append(element)

    return bdas, response

def create(bda):
    payload = bda
    headers = {
        'authorization': 'Bearer ' + _get_token(),
        'content-type': 'application/json'
    }
    response = requests.request("POST", url = read_var('URL_BASE') + read_var('URL_APPS'), headers=headers, data=json.dumps(payload))
    return response
    