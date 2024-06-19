from requests import post
from warnings import warn

def run_psg(cfg_file, type = 'rad', out_file = 'temp.txt', local = True, verbose = True):
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
    type_list = ['rad', 'noi', 'trn', 'atm', 'str', 'tel', 'srf', 'cfg', 'ret', 'all']
    # Check if type selected exists
    if type not in type_list:
        warn(f'{type} is not a known type, output file will be empty!')
    data = {
        'type': type,
        'file': open(cfg_file).read(),
    }
    if local == True:
        url = 'http://localhost:3000/api.php'
    else:
        url = 'https://psg.gsfc.nasa.gov/api.php'
        warn('PSG is not running locally')
    response = post(url, data=data)                 # 'curl' command
    if verbose == True:
        print(f'PSG is running at {url}')
        print(f'type = {type}')
        print(f'Input file: {cfg_file}')
        print(f'Output file: {out_file}')
    with open(out_file, 'w') as ofile:
        ofile.write(response.text)                  # write to output file
