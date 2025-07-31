import requests
import json
from .utils import read_var, update_config_property


def _get_token():
    if read_var("token") is not None:
        return read_var("token")
    else:
        if read_var("username") is not None and read_var("password") is not None: 
            token, _ = get_token(read_var("username"), read_var("password"))
            return token
        else:
            print("WARKING: no token found, please set user and password ENV variables!")

def get_token(user, password):

    payload = 'client_secret=' + read_var('INSTANCE_CLIENT_SECRET') + '&client_id=' + read_var('INSTANCE_CLIENT_ID') + '&grant_type=password&scope=openid&username='+ user +'&password=' + password
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url=read_var("url_login"), headers=headers, data=payload)

    try:
        token = json.loads(response.text)['access_token']
    except:
        token = None
    
    update_config_property(prop="token", value=token)
    
    return token, response
