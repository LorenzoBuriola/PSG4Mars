import logging
import tomllib

logger = logging.getLogger(__name__)

def read_config(path):
    """
    Read configuration settings from a TOML file.

    Parameters:
    - path (str): Path to the TOML configuration file.

    Returns:
    - dict: Configuration settings as a dictionary.
    """
    try:
        with open(path, "rb") as file:
            config = tomllib.load(file)
        logger.info(f"Configuration loaded successfully from {path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration from {path}: {e}")
        raise