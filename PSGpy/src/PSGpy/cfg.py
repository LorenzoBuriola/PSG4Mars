# read, edit and write cfg files

import numpy as np
import pandas as pd
import re
import json
import os

from PSGpy.run_psg import run_psg
from PSGpy.utils import name_file

def read_cfg(file_path):
    """
    It reads the configuration file
    
    Parameters
    ----------
    file_path: string - path of the configuration file

    Returns
    --------
    variables: dictionary - dictionary of all the variables in configuration file
    """
    # Dictionary to hold the parsed variables and their values
    variables = {}
    # Regular expression to match the pattern <name>value
    pattern = re.compile(r'<(.*?)>(.*)')
    # Read the file line by line
    with open(file_path, 'r') as file:
        for line in file:
            match = pattern.match(line.strip())
            if match:
                # Extract the variable name and value
                name, value = match.groups()
                variables[name] = value
    return variables

def cfg_to_json(file_path):
    """
    It reads the configuration file and writes it in a JSON format
    
    Parameters
    ----------
    file_path: string - path of the configuration file
    """
    # Using of the function read_cfg that read
    variables = read_cfg(file_path)        
    # Changing extension
    base_name,_ = os.path.splitext(file_path)   
    new_name = f'{base_name}.json'
    with open(new_name, 'w') as ofile:
        json.dump(variables,ofile)
    return

def dict_to_cfg(dictionary, file_path):
    """
    It writes a dictionary to a configuration file for PSG (.txt)

    Parameters
    ----------
    dd: dictionay - data to write
    file_path: string - path of the configuration file
    """
    with open(file_path, 'w') as ofile:
        for key in dictionary:
            ofile.write(f'<{key}>{dictionary[key]}\n')
    return

def read_atm_layers(cfg_dict):
    n_layer = int(cfg_dict['ATMOSPHERE-LAYERS'])
    names = 'Pressure,Temperature,'+cfg_dict['ATMOSPHERE-LAYERS-MOLECULES']
    names = names.split(',')
    tab = np.zeros((n_layer, len(names)))
    for i in range(n_layer):
        tab[i,:] = np.fromstring(cfg_dict[f'ATMOSPHERE-LAYER-{i+1}'],sep=',')
    tab_df = pd.DataFrame(tab, columns=names)

    #TODO aggiungere trattazione dell'unita di misura

    return tab_df

def write_atm_layers(df, cfg_dict):
    n_layer = df.shape[0]
    cfg_dict['ATMOSPHERE-LAYERS'] = n_layer
    names = df.columns
    cfg_dict['ATMOSPHERE-LAYERS-MOLECULES'] = ",".join(names[2:])
    for i in range(n_layer):
        cfg_dict[f'ATMOSPHERE-LAYER-{i+1}'] = ','.join(str(n) for n in df.iloc[i,:].to_list())


def generate_profile(cfg_dict, date, latitude, longitude, opath) -> None:
    cfg_dict['OBJECT-DATE'] = date
    cfg_dict['OBJECT-OBS-LATITUDE'] = latitude
    cfg_dict['OBJECT-OBS-LONGITUDE'] = longitude
    dict_to_cfg(dictionary=cfg_dict, file_path='cfg_temp.txt')
    run_psg(cfg_file='cfg_temp.txt', type='cfg', wephm = 'y', watm='y', 
                    out_file=f"{opath}{name_file('cfg', date, latitude, longitude)}.txt", verbose=False)