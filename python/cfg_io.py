#Lorenzo Buriola - 12 giugno 2024

# Script with utilities for reading and writing configuration files of PSG

import re
import json
import os

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

