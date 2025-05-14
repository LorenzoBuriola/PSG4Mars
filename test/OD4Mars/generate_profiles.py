# Lorenzo Buriola - University of Bologna, CNR-ISAC
# The function will create a profile for each combination of latitude, longitude, and date
# in the specified output path.
# 1 in pipeline

import numpy as np
import pandas as pd
import pypsg.cfg as cfg

def generate_profiles(latitudes, longitudes, dates, opath, ipath='basic_cfg.txt',
                      verbose = False) -> None:
    dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()
    cfg_df = cfg.read_cfg(ipath)
    for date in dates_list:
        for lat in latitudes:
            for long in longitudes:
                if verbose:
                    print(f"Generating profile for date: {date}, lat: {lat}, long: {long}")
                cfg.generate_profile(cfg_df, date, lat, long, opath=opath)


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

opath = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/profiles/'
ipath = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/basic_cfg.txt'

# Generate profiles
print("Generating profiles...")
generate_profiles(latitudes, longitudes, dates, opath, ipath, verbose=True)
print("Profiles generated successfully.")
