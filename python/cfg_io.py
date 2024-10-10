#Lorenzo Buriola - 12 giugno 2024

# Script with utilities for reading and writing configuration files of PSG

import re
import json
import os

import numpy as np
import pandas as pd

import atm_obj
import run_psg
from utils import transform_date

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

def define_atmosphere(cfg_dict, gglist, alist, otherlist):
    cfg = cfg_dict
    #TODO aggiungere gas non in datatbase senza profilo
    #gas
    gunit = []
    gabun = []
    gtype = []
    for gname in gglist:
        gg = atm_obj.gas(name=gname,abun='1',unit='scl')
        gunit.append(gg.unit)
        gabun.append(gg.abun)
        gtype.append(gg.code)
    cfg['ATMOSPHERE-GAS'] = ','.join(gglist)
    cfg['ATMOSPHERE-UNIT'] = ','.join(gunit)
    cfg['ATMOSPHERE-ABUN'] = ','.join(gabun)
    cfg['ATMOSPHERE-TYPE'] = ','.join(gtype)
    cfg['ATMOSPHERE-NGAS'] = len(gglist)
    #aerosol
    aunit = []
    aabun = []
    asize = []
    asunit = []
    atype = []
    for aname in alist:
        aer = atm_obj.aeros(name=aname,abun='1',unit='scl',size=1,sunit='scl', type='CRISM_Wolff')
        aunit.append(aer.unit)
        aabun.append(aer.abun)
        asize.append(aer.size)
        asunit.append(aer.sunit)
        atype.append(aer.type)
    cfg['ATMOSPHERE-AEROS'] = ','.join(alist)
    cfg['ATMOSPHERE-AUNIT'] = ','.join(aunit)
    cfg['ATMOSPHERE-AABUN'] = ','.join(aabun)
    cfg['ATMOSPHERE-ASIZE'] = ','.join(asize)
    cfg['ATMOSPHERE-ASUNI'] = ','.join(asunit)
    cfg['ATMOSPHERE-NAERO'] = len(alist)
    cfg['ATMOSPHERE-ATYPE'] = ','.join(atype)
    #other
    cfg['ATMOSPHERE-CONTINUUM'] = ','.join(otherlist)

    return cfg

"""
def generate_profile(cfg_dict, date, latitude, longitude, opath) -> None:
    cfg_dict['OBJECT-DATE'] = date
    cfg_dict['OBJECT-OBS-LATITUDE'] = latitude
    cfg_dict['OBJECT-OBS-LATITUDE'] = longitude
    dict_to_cfg(dictionary=cfg_dict, file_path='cfg_temp.txt')
    run_psg.run_psg(cfg_file='cfg_temp.txt',type='cfg', wephm = 'y', watm='y', 
                    out_file=f'{opath}cfg_{latitude}_{longitude}_{transform_date(date)}.txt', verbose=False)

    cfg = read_cfg('cfg_temp.txt')
    ps = cfg['ATMOSPHERE-PRESSURE']
"""