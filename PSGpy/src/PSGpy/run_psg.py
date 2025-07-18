# *******************************************************
# Lorenzo Buriola - University of Bologna - CNR-ISAC
# PSGpy - run_psg.py
# Python wrapper for run PSG within python apps
# ******************************************************* 

import PSGpy.docker_utils as docker_utils
from requests import post
from warnings import warn

def run_psg(cfg_file, out_file = 'temp.txt', 
            type = 'rad', wgeo = 'y', wephm = 'n', watm = 'n', whdr = 'y',
            local = True, verbose = True):
    """
    It runs PSG requesting to http

    Parameters
    ----------
    cfg_file: string - path of the configuration file
    type: string - type of output wanted, default is Radiance (rad)
    out_file: string - path of the output file
    local: boolean - if run psg locally or not, default is yes (not local run will raise a warning)
    verbose: boolean - if print details, default is yes
    """

    # Check if type selected exists
    type_list = ['rad', 'noi', 'trn', 'atm', 'str', 'tel', 'srf', 'cfg', 'ret', 'lyo', 'lyr', 'all']
    if type not in type_list:
        warn(f'{type} is not a known type, output file will be empty!')

    # Check for wgeo
    if wgeo not in ['y', 'n']:
        warn(f'{wgeo} is not a known type, output file will be empty!')
    
    #Check for wephm
    wephm_list = ['y', 'N', 'T', 'S', 'P', 'n']
    if wephm not in wephm_list:
        warn(f'{wephm} is not a known type, output file will be empty!')

    # Check for watm
    if watm not in ['y', 'n']:
        warn(f'{watm} is not a known type, output file will be empty!')
    
    # Check for watm
    if whdr not in ['y', 'n']:
        warn(f'{whdr} is not a known type, output file will be empty!')
        
    data = {
        'type': type,
        'wgeo' : wgeo,
        'wephm' : wephm,
        'watm' : watm,
        'whdr' : whdr,
        'file': open(cfg_file).read(),
    }
    if local == True:
        url = 'http://localhost:3000/api.php'
        # Check if PSG is running locally
        if not docker_utils.is_container_running('psg', 'unix:///run/user/1007/docker.sock'):
            raise Exception('Container psg is not running, please start container or select local=False')
    else:
        url = 'https://psg.gsfc.nasa.gov/api.php'
    # 'curl' command
    response = post(url, data=data)                 
    if verbose == True:
        print(f'PSG is running at {url}')
        print(f'type = {type}')
        print(f'Input file: {cfg_file}')
        print(f'Output file: {out_file}')
    # write to output file
    with open(out_file, 'w') as ofile:
        ofile.write(response.text)                  
