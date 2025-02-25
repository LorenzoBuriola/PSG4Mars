import xarray as xr
import numpy as np

coeff_path = '/home/buriola/PSG/PSG4Mars/data/coeff/'
od_path = '/home/buriola/PSG/PSG4Mars/data/od/'

gasses = ['CO2','CO' ,'H2O', 'HDO', 'O3', 'HCl']
ranges = np.arange(100,3050,50)

for g_name in gasses:
    print(f'Gas: {g_name}')
    for i in range(len(ranges)-1):
        print(f'Frequency window: {ranges[i]}-{ranges[i+1]}')
        tab = xr.open_dataarray(f'{od_path}{g_name}/od_{g_name}_freq{ranges[i]}_{ranges[i+1]}.nc')
        fit_results = tab.polyfit(dim='DeltaT', deg=3)
        fit_results.to_netcdf(f'{coeff_path}{g_name}/coeff_{g_name}_freq{ranges[i]}_{ranges[i+1]}.nc')
        
        

        
        
