import numpy as np
import pandas as pd
import pypsg.cfg as cfg

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
cfg_path = '../data/cfg/'
cfg_df = cfg.read_cfg(f'{cfg_path}basic_cfg.txt')

for date in dates_list:
    for lat in latitudes:
        for long in longitudes:
            cfg.generate_profile(cfg_df, date, lat, long, opath=f'{cfg_path}/profiles/')