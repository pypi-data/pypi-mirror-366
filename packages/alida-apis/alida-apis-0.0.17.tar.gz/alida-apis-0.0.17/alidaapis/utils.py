import os
from os import listdir

def read_var(name):
    return os.environ.get(name.upper())

def update_config_property(prop, value):
    os.environ[prop.upper()] = value
    

def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]
