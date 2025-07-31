from .utils import read_var
from .auth import _get_token
import requests, json
from .minio_utils import download_folder, upload_folder
import os, shutil
import uuid
import pandas as pd
import alidaapis.datasource as ds
from os import walk
from io import StringIO

def get_metadata(dataset_id):

    url = read_var("URL_BASE") + read_var("URL_DATASETS") + "/" + str(dataset_id)

    payload = {}
    headers = {
        'authorization': 'Bearer ' + _get_token(),
    }

    return requests.request("GET", url, headers=headers, data=payload)

def get_files_in_folder(path):
    filenames = next(walk(path), (None, None, []))[2]
    result = []
    for filename in filenames:
        result.append(os.path.join(path, filename))
    return result 

def head(filename: str, n: int):
    try:
        with open(filename) as f:
            head_lines = [next(f).rstrip() for x in range(n)]
    except StopIteration:
        with open(filename) as f:
            head_lines = f.read().splitlines()
    return head_lines

def check_inconsistencies(path):
    #TODO
    return 

def concat_csv_files_in_folder(folder_path, nrows=10):
    # List to store individual dataframes
    dataframes = []

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Construct full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the file is a CSV
        if file_path.endswith('.csv'):
            # Read the first 10 rows of the CSV file
            df = pd.read_csv(file_path, nrows=nrows)
            dataframes.append(df)
    
    # Concatenate all dataframes
    concatenated_df = pd.concat(dataframes, ignore_index=True)
    
    return concatenated_df


# Starting from a CSV file or a folder of csvs, infer metadata. For folders, rows read are limited to the first 20 of each file.
def get_cols_metadata(path, nrows=20):
    
    if path[:-3]=="csv":
        df = pd.read_csv(path)
    else:
        df = concat_csv_files_in_folder(folder_path=path, nrows=nrows)

    pd_types_to_platform_types = {
        "int64": "Number",
        "float64": "Number",
        "object": "String",
        "bool": "String",
        "datatime": "Date"
    }

    col_types = dict(df.dtypes)

    columns = []
    for col in col_types.keys():
        columns.append({"name": col, "type": pd_types_to_platform_types[str(col_types[col])]})

    return columns


def register(remote_path, name, description=None, datasource_id=None, datasource_name=None, tags=[]):
    """Register a dataset composed of generic files and folders (not a tabular dataset)

    Parameters
    ----------
    remote_path : str
        Path inside the datasource
    name :str
        Name of the dataset
    description: str, optional
        Description of the dataset
    datasource_id: str
        The id of the datasource. If None datasource_name will be used
    datasource_name: str, optional
        The name of the datasource. 
    tags: list<str>, optional
        List of tags.
    Returns
    -------
    Http response
    """
    
    if datasource_id is None:
        datasource = ds.get_by_name(datasource_name)
    elif datasource_name is None: 
        datasource = ds.get_by_id(datasource_id)
    else:
        raise Exception("Please specify either datasource id or datasource name")

    
    url = read_var("URL_BASE") + read_var("URL_DATASETS")
    
    payload = {
        "datasetFileType": {
            "type": "image",
            "path": remote_path
        },
        "datasource": datasource,
        "name": name,
        "description": description,
        "tags": tags
    }
    headers = {
        'authorization': 'Bearer ' + _get_token(),
        'content-type': 'application/json'
    }
    return requests.request("POST", url, headers=headers, data=json.dumps(payload))


    
def register_tabular(remote_path, name, path=None, description=None, columns_metadata=None, datasource_id=None, datasource_name=None, tags=[]):
    if columns_metadata is None:
        columns_metadata = get_cols_metadata(path=path)
    
    if datasource_id is None:
        datasource = ds.get_by_name(datasource_name)
    else: 
        datasource = ds.get_by_id(datasource_id)
    
    url = read_var("URL_BASE") + read_var("URL_DATASETS")

    payload = {
        "datasetFileType": {
            "type": "table",
            "columns": columns_metadata,
            "tableName": remote_path,
            "path": None
        },
        "datasource": datasource,
        "name": name,
        "description": description,
        "tags": tags
    }
    headers = {
        'authorization': 'Bearer ' + _get_token(),
        'content-type': 'application/json'
    }
    return requests.request("POST", url, headers=headers, data=json.dumps(payload))


def upload_and_register_tabular_from_file(path, name, description=None, datasource_id=None, datasource_name=None, tags=[]):
    if datasource_id is None:
        datasource = ds.get_by_name(datasource_name)
    else: 
        datasource = ds.get_by_id(datasource_id)

    single_file = path[-3:]=="csv"
            
    remote_path = str(uuid.uuid4())

    if single_file:
        # create tmp folder
        os.mkdir(remote_path)
        shutil.copy(src=path, dst = remote_path + "/")
        path = remote_path
    
    remote_path = os.path.join(datasource['prefixPath'], remote_path)
    
    endpoint_url = datasource['host'] + ":" + str(datasource['port'])

    # Check if ssl or not
    if not endpoint_url.startswith('http'):
        if datasource['secure']== True:
            endpoint_url = "https://" + endpoint_url
        else:
            endpoint_url = "http://" + endpoint_url
    
    # Upload dataset to Minio
    for result in upload_folder(minio_address=endpoint_url, 
                                minio_access_key=datasource['accessKey'], 
                                minio_secret_key=datasource['secretKey'], 
                                bucket_name=datasource['bucket'], 
                                local_path=path, 
                                remote_path=remote_path):
        pass

    
    response = register_tabular(path=path, 
                                remote_path=remote_path, 
                                name=name, 
                                description=description, 
                                datasource_id=datasource_id, 
                                datasource_name=datasource_name,
                                tags=tags)
    
    # Remove tmp folder
    if single_file:
        shutil.rmtree(path)
   
    return response



def download(dataset_id, local_path="./tmp/data/"):
    
    metadata = json.loads(get_metadata(dataset_id=dataset_id).text)
    datasource = metadata['datasource']
    access_key = datasource['accessKey']
    secret_key = datasource['secretKey']
    bucket_name = datasource['bucket']
    endpoint_url = datasource['host'] + ":" + str(datasource['port'])
    if not endpoint_url.startswith('http'):
        if datasource['secure']== True:
            endpoint_url = "https://" + endpoint_url
        else:
            endpoint_url = "http://" + endpoint_url
    if 'path' in metadata['datasetFileType'] and metadata['datasetFileType']['path'] is not None:
        path = metadata['datasetFileType']['path']
    else:
        path = metadata['datasetFileType']['tableName']

    if path[-1]!="/":
        path+="/"
            
    for result in download_folder(minio_address=endpoint_url, minio_access_key=access_key, minio_secret_key=secret_key, bucket_name=bucket_name, local_path=local_path, remote_path=path):
        pass


def get(order = "id", desc="true", limit=20, page=1):
    url = read_var("URL_BASE") + read_var("URL_DATASETS")
    params = {
        'evaluation': 'false',
        'page': str(page),
        'size': str(limit),
        'sort': order,
        'desc': desc,
    }   
    payload = {}
    headers = {
        'authorization': 'Bearer ' + _get_token()
    }
    
    return json.loads(requests.request("GET", url, headers=headers, params=params, data=payload).text)['content']


def get_by_name(name):
    result = []
    services = get(limit=1000) #TODO Use a better backend method for dataset search
    
    for service in services:
        if service['name'] == name:
            result.append(service)
    return result
