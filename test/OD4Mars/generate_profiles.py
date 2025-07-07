# Lorenzo Buriola - University of Bologna, CNR-ISAC
# The function will create a profile for each combination of latitude, longitude, and date
# in the specified output path.
# 1 in pipeline

import numpy as np
import pandas as pd
import PSGpy.cfg as cfg

def generate_profile(cfg_dict, date, latitude, longitude, opath) -> None:
    cfg_dict['OBJECT-DATE'] = date
    cfg_dict['OBJECT-OBS-LATITUDE'] = latitude
    cfg_dict['OBJECT-OBS-LONGITUDE'] = longitude
    dict_to_cfg(dictionary=cfg_dict, file_path='cfg_temp.txt')
    run_psg(cfg_file='cfg_temp.txt', type='cfg', wephm = 'y', watm='y', 
                    out_file=f"{opath}{name_file('cfg', date, latitude, longitude)}.txt", verbose=False)

def generate_profiles_2(latitudes, longitudes, dates, opath, ipath='basic_cfg.txt',
                      verbose = False) -> None:
    dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()
    cfg_df = cfg.read_cfg(ipath)
    for date in dates_list:
        for lat in latitudes:
            for long in longitudes:
                if verbose:
                    print(f"Generating profile for date: {date}, lat: {lat}, long: {long}")
                generate_profile(cfg_df, date, lat, long, opath=opath)

# INPUTS
latitudes = np.linspace(-90, 90, 49)
longitudes = np.linspace(0, 360, 65)[:-1]

start_date = '2019-03-24'
end_date = '2021-02-08'
dates = pd.date_range(
    start=start_date,
    end=end_date,
    periods=24,
    unit='s'
)

opath = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/profiles/'
ipath = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/basic_cfg.txt'

# Generate profiles
print("Generating profiles...")
generate_profiles_2(latitudes, longitudes, dates, opath, ipath, verbose=True)
print("Profiles generated successfully.")
