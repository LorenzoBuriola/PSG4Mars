import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def prepare_directories(config) -> None:
    """
    Prepare the necessary directories for the OD4Mars program.

    Parameters:
    - config (dict): Configuration dictionary containing the paths and gas list.

    Returns:
    None
    """

    data_path = Path(config['data_path'])
    gas_list = config['gas_list']

    # Centralize all directory roots so creation stays consistent.
    directories = {
        'cfg': data_path / 'cfg',
        'lyr': data_path / 'lyr',
        'lyo': data_path / 'lyo',
        'od': data_path / 'od',
        'coeff': data_path / 'coeff',
        's4Mars': data_path / 's4Mars',
        'output': Path(__file__).resolve().parents[1] / 'output',
        'profiles': Path(config['profiles']['path']),
    }

    for path in directories.values():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug("Directory created or already exists: %s", path)

    # Each gas gets its own subdirectory under the per-product output trees.
    for base_path in [directories['lyr'], directories['lyo'], directories['od'], directories['coeff']]:
        for gas in gas_list:
            gas_path = base_path / gas
            gas_path.mkdir(parents=True, exist_ok=True)
            logger.debug("Subdirectory created or already exists for gas '%s': %s", gas, gas_path)

    (directories['cfg'] / 'OD_gen').mkdir(parents=True, exist_ok=True)

    name_database = config['s4Mars']['name_od_database']
    (directories['s4Mars'] / name_database / 'to_pack').mkdir(parents=True, exist_ok=True)
