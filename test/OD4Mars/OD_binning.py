import numpy as np
import xarray as xr
import os

import PSGpy.OD as OD
from PSGpy.utils import read_out

gasses = ['CO2','CO', 'H2O', 'HDO', 'O3', 'HCl']
ranges = np.arange(89.995, 3049.995, 40)  # Frequency ranges in cm-1
#ranges = np.arange(100, 3050, 50)
DTs = np.arange(-60, 70, 10)

lyo_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/lyo/'
od_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/od/'

tab = read_out(f'{lyo_path}CO2/lyo_CO2_0_freq90_130.txt')
hh = tab.columns[1:-1].to_numpy(dtype='float64')

for g_name in gasses:
    print(f'Gas: {g_name}')
    for i in range(len(ranges)-1):
        path = f'{od_path}{g_name}/od_{g_name}_freq{ranges[i]+0.005:.0f}_{ranges[i+1]+0.005:.0f}.nc'
        if os.path.exists(path):
            continue
        print(f'Frequency window: {ranges[i]}-{ranges[i+1]}')
        print('Computing OD...')
        EE = False
        low_freqs = np.arange(ranges[i], ranges[i+1],1e-2) + 0.005
        list_of_od = []
        list_of_errors = []
        list_of_hr = []
        for DT in DTs:
            print(f'Temperature shift: {DT}')
            try:
                tab = read_out(f'{lyo_path}{g_name}/lyo_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}.txt')
                tab = OD.OD_compute(tab)
                hr = tab.loc[tab.freq.round(decimals = 4).isin(low_freqs.round(decimals =2))].iloc[:,1:]
                tab,err = OD.OD_binning(tab, low_freqs)
                list_of_od.append(tab)
                list_of_errors.append(err)
                list_of_hr.append(hr)
            except ValueError as ERROR:
                print("An exception occurred:", type(ERROR).__name__, "–", ERROR)
                EE = True
        if EE:
            continue
        aa = np.stack(list_of_od, axis=-1)
        ss = np.stack(list_of_errors, axis=-1)
        xhr = np.stack(list_of_hr, axis=-1)
        aa = xr.DataArray(data=aa, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                freq = low_freqs,
                altitude = hh,
                DeltaT = DTs
            ))
        ss = xr.DataArray(data=ss, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                freq = low_freqs,
                altitude = hh,
                DeltaT = DTs
            ))
        xhr = xr.DataArray(data=xhr, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                freq = low_freqs,
                altitude = hh,
                DeltaT = DTs
            ))
        ds = xr.Dataset({
            'od': aa,
            'error': ss,
            'hr_od': xhr
        })
        ds.to_netcdf(path)

print('All done!')