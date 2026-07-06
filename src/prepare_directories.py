from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

def prepare_directories(config) -> None:
    """
    Prepare the necessary directories for the OD4Mars program.

    Parameters:
    - base_path (str): The base path where the directories will be created.
    - gas_list (list): List of gas names for which directories will be created.

    Returns:
    None
    """

    data_path = config['data_path']
    # Define the paths for various directories
    cfg_path = os.path.join(data_path, 'cfg/')
    lyr_path = os.path.join(data_path, 'lyr/')
    lyo_path = os.path.join(data_path, 'lyo/')
    od_path = os.path.join(data_path, 'od/')
    coeff_path = os.path.join(data_path, 'coeff/')
    s4Mars_path = os.path.join(data_path, 's4Mars/')

    # Create the directories if they don't exist
    for path in [cfg_path, lyr_path, lyo_path, od_path, coeff_path, s4Mars_path]:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory created or already exists: {path}")

    # Create subdirectories for each gas in the lyr and lyo directories
    gas_list = config['gas_list']
    for path in [lyr_path, lyo_path, od_path, coeff_path]:
        for gas in gas_list:
            gas_path = os.path.join(path, gas)
            Path(gas_path).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Subdirectory created or already exists for gas '{gas}': {gas_path}")

    #output path
    Path('/home/buriola/OD4Mars/output/').mkdir(exist_ok=True)

    profile_path = config['profiles']['path']
    Path(profile_path).mkdir(exist_ok=True)

    Path(f'{cfg_path}OD_gen/').mkdir(exist_ok=True)
    
    name_database = config['s4Mars']['name_od_database']
    outdir = Path(s4Mars_path+name_database+'/to_pack/')
    outdir.mkdir(parents=True, exist_ok=True)
