import numpy as np
import xarray as xr
import os

import pypsg.OD as OD
from pypsg.utils import read_out


gasses = ['CO2', 'CO', 'H2O', 'HDO', 'O3', 'HCl']
ranges = np.arange(100,3050,50)
DTs = np.arange(-60, 70, 10)

lyo_path = '/home/buriola/PSG/PSG4Mars/data/lyo/'
od_path = '/home/buriola/PSG/PSG4Mars/data/od/'

tab = read_out(f'{lyo_path}CO2/lyo_CO2_0_freq100_150.txt')
hh = tab.columns[1:-1].to_numpy(dtype='float64')

for g_name in gasses:
    print(f'Gas: {g_name}')
    for i in range(len(ranges)-1):
        path = f'{od_path}{g_name}/od_{g_name}_freq{ranges[i]}_{ranges[i+1]}.nc'
        print(f'Frequency window: {ranges[i]}-{ranges[i+1]}')
        if not os.path.exists(path):
            ee = False
            freqs = np.arange(ranges[i], ranges[i+1],1e-4) + 1e-4
            low_freqs = np.arange(ranges[i], ranges[i+1],1e-2) + 1e-2
            list_of_arrays = []
            for DT in DTs:
                print(f'Temperature shift: {DT}')
                try:
                    tab = read_out(f'{lyo_path}{g_name}/lyo_{g_name}_{DT}_freq{ranges[i]}_{ranges[i+1]}.txt')
                    tab = OD.OD_compute(tab)
                    tab = OD.OD_binning(tab, low_freqs)
                    tab = tab.to_numpy()[:,1:]
                    list_of_arrays.append(tab)
                except ValueError as error:
                    print("An exception occurred:", type(error).__name__, "–", error)
                    ee = True
            if ee:
                continue
            else:
                aa = np.stack(list_of_arrays, axis=-1)
                aa = xr.DataArray(data=aa, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                    freq = low_freqs,
                    altitude = hh,
                    DeltaT = DTs
                ))
            aa.to_netcdf(path)