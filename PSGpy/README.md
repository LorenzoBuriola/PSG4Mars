# PSGpy

This is a Python package developed for work with the Planetary Spectrum Generator (PSG) radiative transfer suite by NASA. The purpose of this package is to easily launch radiative simulation with PSG within python apps. PSGpy offers different functions to write and edit configuration files, run PSG and deal with its outputs. To install the package PSGpy, inside the PSGpy directory, just run `pip install .`.

The package contains:
* `docker_utils.py`: contains python function that makes use of the Docker SDK for Python (https://docker-py.readthedocs.io/en/stable/#) for start and stop PSG container from within Python apps.
* `run_psg.py`: a python wrapper for the API commands for launch PSG simulation both on local machine and online.
* `cfg.py`: collection of functions for managing the configuration files for PSG
* `atm_obj.py`: contains new defined classes (gas, aeros, atmosphere) used to easily edit the atmospheric settings of the configuration file.
* `utils.py`: contains miscellaneous functions.