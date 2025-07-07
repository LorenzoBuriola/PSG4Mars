# *******************************************************
# Lorenzo Buriola - University of Bologna - CNR-ISAC
# PSGpy - cfg.py
# Functions that deal with PSG configuration files
# *******************************************************

import numpy as np
import pandas as pd
import re
import json
import os

from PSGpy.run_psg import run_psg
from PSGpy.utils import name_file

def read_cfg(file_path):
    """
    It reads the configuration fil and return a pyhton dictionary
    
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

def dict_to_cfg(cfg_dict, file_path):
    """
    It writes a dictionary to a configuration file for PSG (.txt)

    Parameters
    ----------
    cfg_dict: dictionay - data to write
    file_path: string - path of the configuration file
    """
    with open(file_path, 'w') as ofile:
        for key in cfg_dict:
            ofile.write(f'<{key}>{cfg_dict[key]}\n')
    return

def read_atm_layers(cfg_dict):
    """
    Reads specifically the atmospheric layers of a configuration file and 
    returns a pandas Dataframe

    Parameters
    ----------
    cfg_dict: dictionary 
    """
    n_layer = int(cfg_dict['ATMOSPHERE-LAYERS'])
    names = 'Pressure,Temperature,'+cfg_dict['ATMOSPHERE-LAYERS-MOLECULES']
    names = names.split(',')
    tab = np.zeros((n_layer, len(names)))
    for i in range(n_layer):
        tab[i,:] = np.fromstring(cfg_dict[f'ATMOSPHERE-LAYER-{i+1}'],sep=',')
    tab_df = pd.DataFrame(tab, columns=names)

    #TODO aggiungere trattazione dell'unita di misura
    return tab_df

def write_atm_layers(atm_df, cfg_dict):
    """
    Write specifically the atmospheric layers of a configuration file

    Parameters
    ----------
    atm_df: DtaFrame - atmospehric layers
    cfg_dict: dictionary 
    """
    n_layer = atm_df.shape[0]
    cfg_dict['ATMOSPHERE-LAYERS'] = n_layer
    names = atm_df.columns
    cfg_dict['ATMOSPHERE-LAYERS-MOLECULES'] = ",".join(names[2:])
    for i in range(n_layer):
        cfg_dict[f'ATMOSPHERE-LAYER-{i+1}'] = ','.join(str(n) for n in atm_df.iloc[i,:].to_list())


