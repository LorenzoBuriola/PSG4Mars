import logging
import numpy as np
import xarray as xr
from PSGpy.utils import read_out
import src.OD as OD

logger = logging.getLogger(__name__)

def OD_binning(gas_list, ranges, temperatures, lyo_path, od_path):
    tab = read_out(f'{lyo_path}CO2/lyo_CO2_0_freq90_130.txt')
    hh = tab.columns[1:-1].to_numpy(dtype='float64')
    for g_name in gas_list:
        logger.info(f'Gas: {g_name}')
        for i in range(len(ranges)-1):
            path = f'{od_path}{g_name}/od_{g_name}_freq{ranges[i]+0.005:.0f}_{ranges[i+1]+0.005:.0f}.nc'
            logger.info(f'Frequency window: {ranges[i]}-{ranges[i+1]}')
            EE = False
            low_freqs = np.arange(ranges[i], ranges[i+1], 1e-2) + 0.005
            list_of_od = []
            list_of_errors = []
            for DT in temperatures:
                logger.info(f'Temperature shift: {DT}')
                try:
                    tab = read_out(f'{lyo_path}{g_name}/lyo_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}.txt')
                    tab = tab[:400009] # Limit to the first 400009 rows
                    tab = OD.OD_compute(tab)
                    tab,err = OD.OD_binning(tab, low_freqs)
                    list_of_od.append(tab)
                    list_of_errors.append(err)
                except ValueError as ERROR:
                    logger.info("An exception occurred:", type(ERROR).__name__, "–", ERROR)
                    EE = True
            if EE:
                continue
            aa = np.stack(list_of_od, axis=-1)
            ss = np.stack(list_of_errors, axis=-1)

            
            aa = xr.DataArray(data=aa, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                    freq = low_freqs,
                    altitude = hh,
                    DeltaT = temperatures
                ))
            ss = xr.DataArray(data=ss, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                    freq = low_freqs,
                    altitude = hh,
                    DeltaT = temperatures
                ))
            ds = xr.Dataset({
                'od': aa,
                'error': ss,
            })
            ds.to_netcdf(path)

    logger.info('All done!')