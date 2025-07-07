import numpy as np
import pandas as pd
import PSGpy.cfg as cfg
from PSGpy.utils import name_file

def custom_edges(aa, nbin):
    nn = len(aa)
    return np.interp(np.linspace(0, nn, nbin + 1),
                     np.arange(nn),
                     np.sort(aa))

def generate_p_levels(latitudes, longitudes, dates, ipath, ofile = 'p_edges.npy',
                      verbose = False):
    dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()
    p = []
    for date in dates_list:
        for lat in latitudes:
            for long in longitudes:
                temp_cfg = cfg.read_cfg(f"{ipath}{name_file('cfg', date, lat, long)}.txt")
                temp_df = cfg.read_atm_layers(temp_cfg)
                p.append(temp_df.Pressure)
    p = np.asarray(p)
    pcut1 = 1e-8
    pcut2 = 1e-3
    plow = p[p <= pcut1]
    e_low = custom_edges(plow, 5)
    p_med = p[(p>pcut1) & (p<pcut2)]
    e_med = custom_edges(p_med, 20)[1:-1]  # Exclude the last edge to avoid duplication
    p_high = p[p>=pcut2]
    e_high = custom_edges(p_high,30)
    ee = np.unique(np.concatenate([e_low,e_med,e_high]))

    if verbose:
        print('******************************')
        print(f"Pressure levels generated:")
        for i in range(len(ee)):
            print(f"Level {i+1}:\t{ee[i]:.3e}")
    if ofile is not None:
        np.save(ofile, ee)
    return ee

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
ipath = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/profiles/'

# Generate pressure levels
print("Generating pressure levels...")
p_levels = generate_p_levels(latitudes, longitudes, dates, ipath, verbose=True)
print("Pressure levels generated successfully.")