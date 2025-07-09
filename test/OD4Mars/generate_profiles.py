# Lorenzo Buriola - University of Bologna, CNR-ISAC
# The function will create a profile for each combination of latitude, longitude, and date
# in the specified output path.
# 1 in pipeline

import numpy as np
import pandas as pd
import PSGpy.cfg as cfg
from PSGpy.run_psg import run_psg
from PSGpy.utils import name_file

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
dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()

opath = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/profiles/'

# Generate profiles
print("Generating profiles...")
cfg_df = {
    'OBJECT' : 'Planet',
    'OBJECT-NAME' : 'Mars',
}

for date in dates_list:
    for lat in latitudes:
        for long in longitudes:
            print(f"Generating profile for date: {date}, lat: {lat}, long: {long}")
            cfg_df['OBJECT-DATE'] = date
            cfg_df['OBJECT-OBS-LATITUDE'] = lat
            cfg_df['OBJECT-OBS-LONGITUDE'] = long
            cfg.dict_to_cfg(cfg_dict=cfg_df, file_path='cfg_temp.txt')
            run_psg(cfg_file='cfg_temp.txt', type='cfg', wephm = 'y', watm='y', wgeo='n',
                out_file=f"{opath}{name_file('cfg', date, lat, long)}.txt", verbose=False)
print("Profiles generated successfully.")

