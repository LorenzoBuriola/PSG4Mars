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
        mask0 = tab.max(dim='DeltaT') < 1e-8
        mask = mask0.expand_dims({'DeltaT':13})
        tab = xr.where(mask,  0, tab)
        p2 = tab.polyfit(dim='DeltaT', deg=2, full=True)
        p3 = tab.polyfit(dim='DeltaT', deg=3, full=True)
        RMSE2 = (p2.polyfit_residuals/13)**0.5
        RMSE3 = (p3.polyfit_residuals/13)**0.5
        p2 = p2.rename_vars({var: f"{var}_2" for var in p2.data_vars})
        p3 = p3.rename_vars({var: f"{var}_3" for var in p3.data_vars})
        ds = xr.merge([p2, p3])
        ds.assign(mask0 = mask0)
        ds.assign(RMSE2 = RMSE2)
        ds.assign(RMSE3 = RMSE3)
        ds.to_netcdf(f'{coeff_path}{g_name}/coeff_{g_name}_freq{ranges[i]}_{ranges[i+1]}.nc')
        
        

        
        
