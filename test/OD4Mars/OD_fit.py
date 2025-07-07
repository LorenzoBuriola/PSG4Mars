import xarray as xr
import numpy as np

coeff_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/coeff/'
od_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/od/'

#gasses = ['CO2']
gasses = ['CO2', 'CO' ,'H2O', 'HDO', 'O3', 'HCl']
#ranges = np.arange(100, 3050, 50)
ranges = np.arange(90, 3050, 40)

for g_name in gasses:
    print(f'Gas: {g_name}')
    for i in range(len(ranges)-1):
        print(f'Frequency window: {ranges[i]}-{ranges[i+1]}')
        ds = xr.open_dataset(f'{od_path}{g_name}/od_{g_name}_freq{ranges[i]}_{ranges[i+1]}.nc')
        ds.sel(DeltaT = slice(-50,50))
        od = ds.od
        error = ds.error
        error = xr.where(error < 1e-8, 1e-8, error)

        mask0 = od.min(dim='DeltaT') > 1e-8
        #mask_temp = mask0.expand_dims({'DeltaT':13})
        od = xr.where(mask0,  od, 0)

        mask1 = od.min(dim='DeltaT') > 1e-4
        mask1 = mask1

        list_p = []
        list_score = []
        list_chi = []

        for j in [2,3]:
            pp = od.polyfit(dim='DeltaT', deg=j)
            coeffs = pp.polyfit_coefficients
            fitted = xr.polyval(od.DeltaT, coeffs)

            ss_res = ((od - fitted) ** 2).sum(dim='DeltaT')
            ss_tot = ((od - od.mean(dim='DeltaT')) ** 2).sum(dim='DeltaT')
            r2 = 1 - ss_res / ss_tot
            
            chi = (((od - fitted)/error) ** 2).sum(dim='DeltaT')
            dof = 13 - j - 1
            chi = chi / dof
            list_chi.append(chi.rename(f'chi2_{j}'))

            list_p.append(coeffs.rename(f'coeffs_{j}'))
            list_score.append(r2)
        
        ds = xr.merge(list_p)
        ds = ds.assign(mask0 = mask0,
                       mask1 = mask1,
                       score2 = list_score[0],
                       score3 = list_score[1],
                       chi2_2 = list_chi[0], 
                       chi2_3 = list_chi[1])
        ds.to_netcdf(f'{coeff_path}{g_name}/coeff_{g_name}_freq{ranges[i]}_{ranges[i+1]}.nc')


print('Done')
        
        

        
        
