import logging
from pathlib import Path
import numpy as np
import xarray as xr
import pandas as pd
from PSGpy.utils import read_out

logger = logging.getLogger(__name__)

def OD_calc(gas_list, ranges, temperatures, lyo_path, od_path, high_res, low_res, bin = True, cumulative='layer'):
    lyo_path = Path(lyo_path)
    od_path = Path(od_path)
    if high_res != 1e-4:
        bin = False
        logger.warning(f'High resolution is not 1e-4, binning will be disabled')
    tab = read_out(str(lyo_path / 'CO2' / f'lyo_CO2_0.0_freq90_130_{high_res:.0e}.txt'))
    hh = tab.columns[1:].to_numpy(dtype='float64')
    limit = int(40/high_res)
    for g_name in gas_list:
        logger.info(f'Gas: {g_name}')
        for i in range(len(ranges)-1):
            logger.info(f'Frequency window: {ranges[i]}-{ranges[i+1]}')
            list_of_od = []
            list_of_mask = []
            for DT in temperatures:
                logger.info(f'Temperature shift: {DT}')
                tab = read_out(str(lyo_path / g_name / f'lyo_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}_{high_res:.0e}.txt'))
                tab = tab[:limit] # Limit to the first 400000 rows
                tab = OD_compute(tab, altitude=hh)
                high_freqs = tab.freq.to_numpy()[::-1]
                logger.debug(f'Number of high resolution frequencies: {len(high_freqs)}')
                logger.debug(f'Lower frequency: {high_freqs[0]:.4f}, upper frequency: {high_freqs[-1]:.4f}')
                od = tab.iloc[:,1:].to_numpy(dtype='float64')[::-1,:]
                if low_res <= 1e-4 or not bin:
                    low_res = max(1e-4, low_res)
                    logger.debug(f'Low resolution: {low_res:.0e}, no binning applied')
                    low_freqs = high_freqs
                    mask = np.ones(od.shape, dtype=bool)
                else:
                    logger.debug(f'Low resolution: {low_res:.0e}, applying binning')
                    low_freqs = np.arange(high_freqs[0]+low_res/2-high_res, high_freqs[-1], low_res)
                    logger.debug(f'Number of low resolution frequencies: {len(low_freqs)}')
                    logger.debug(f'Lower frequency: {low_freqs[0]:.4f}, upper frequency: {low_freqs[-1]:.4f}')
                    od, mask = OD_binning(od, int(low_res/high_res), cumulative=cumulative)
                list_of_od.append(od)
                list_of_mask.append(mask)
            try:
                aa = np.stack(list_of_od, axis=-1)
                mm = np.stack(list_of_mask, axis=-1)
            except ValueError as e:
                logger.error(f'Error stacking arrays for frequency window {ranges[i]}-{ranges[i+1]}: {e}')
                continue

            aa = xr.DataArray(data=aa, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                    freq = low_freqs,
                    altitude = hh[:aa.shape[1]],
                    DeltaT = temperatures
                ))
            mm = xr.DataArray(data=mm, dims=['freq', 'altitude', 'DeltaT'], coords=dict(
                    freq = low_freqs,
                    altitude = hh[:mm.shape[1]],
                    DeltaT = temperatures
                ))
            ds = xr.Dataset({
                'od': aa,
                'mask': mm
            })
            path = od_path / g_name / f'od_{g_name}_freq{ranges[i]+0.005:.0f}_{ranges[i+1]+0.005:.0f}_{low_res:.0e}_{cumulative}.nc'
            ds.to_netcdf(path, engine='netcdf4', mode='w')
    logger.info('All done!')
 
def OD_compute(data, altitude=None):
    arr = data.to_numpy(dtype='float64')
    if altitude is None:
        altitude = data.columns[1:].to_numpy(dtype='float64')
    paths = np.diff(altitude)
    out = arr[:,:-1].copy()
    out[:,1:] *= paths
    names = ['freq'] + [f'level_{i+1}' for i in range(out.shape[1]-1)]
    return pd.DataFrame(data=out, columns=names)
    
def OD_binning(high_res, res_ratio, cumulative='layer'):
    """
    Bins the high resolution optical depth data to a lower resolution.
    Parameters:
    high_res (np.ndarray): High resolution optical depth data (frequency, altitude).
    res_ratio (int): The ratio of high resolution to low resolution.
    cumulative (str): The method for cumulative transmittance calculation. Options are 'top', 'bottom', 'layer', or 'od'.
    Returns:
    np.ndarray: Binned optical depth data.
    np.ndarray: Mask indicating points binned with top or bottom method (valid only for those methods).
    """
    ods = high_res.T                                                       #Transpose to have altitude as the first dimension
    if cumulative != 'od':
        #Compute transmittance and cumulative transmittance
        trn = np.exp(-ods)
        binned = trn.reshape(trn.shape[0], -1, res_ratio).mean(axis=2)
        logger.debug(f'Binned transmittance shape: {binned.shape}')
        mask = np.zeros_like(binned, dtype=bool)
        if cumulative in ['top', 'bottom']:
            if cumulative == 'top':
                #Cumulative transmittance from the top of the atmosphere:
                #need to reverse the order of the array to compute the cumulative product from the top 
                #and reverse it back to the original order: index 0 corresponds to the lowest altitude)
                cum_trn = np.cumprod(trn[::-1,:], axis=0)[::-1,:]
                #Compute the mean of the cumulative transmittance and extract the edges of the bins
                #cum_binned,_,_ = binned_statistic(x=f_high,values=cum_trn,statistic='mean',bins=n_bins)
                cum_binned = cum_trn.reshape(cum_trn.shape[0], -1, res_ratio).mean(axis=2)
                #Compute the mean of the transmittance
                #Mask to avoid division buy zero 
                mask[1:] = cum_binned[1:] != 0
                mmask = mask[1:]
                #Compute the transmittance from the binned cumulative transmittance
                #and set the values to the optical depth array
                num = cum_binned[:-1]
                den = cum_binned[1:]
                out = binned[:-1]
            elif cumulative == 'bottom':
                #Similiar to the 'top' case, but cumulative transmittance is computed from the bottom of the atmosphere
                cum_trn = np.cumprod(trn, axis=0)
                #Compute the mean of the cumulative transmittance and extract the edges of the bins
                cum_binned = cum_trn.reshape(cum_trn.shape[0], -1, res_ratio).mean(axis=2)
                #Mask to avoid division buy zero 
                mask[:-1] = cum_binned[:-1] != 0
                mmask = mask[:-1]
                #Compute the transmittance from the binned cumulative transmittance
                #and set the values to the optical depth array
                num = cum_binned[1:]
                den = cum_binned[:-1]
                out = binned[1:]
            np.divide(num, den, out=out, where=mmask)
        #Clip the binned transmittance to avoid log of zero and compute the optical depth
        binned = np.clip(binned, 1e-300, 1.0)
        od_bin = -np.log(binned)

    elif cumulative == 'od':
        #od_bin,edges,_ = binned_statistic(x=f_high,values=ods,statistic='mean',bins=n_bins)
        od_bin = ods.reshape(ods.shape[0], -1, res_ratio).mean(axis=2)
        mask = np.zeros_like(od_bin, dtype=bool)

    return od_bin.T, mask.T

"""
    #Compute the error
    NN = np.sqrt(f_high.size/n_bins)
    pr_error,_,_ = binned_statistic(x=f_high,values=trn,statistic='std',bins=n_bins)
    pr_error = pr_error/NN
    #sec_error,_,_ = binned_statistic(x=f_high,values=ods,statistic='std',bins=n_bins)
    #error = sec_error
    error = pr_error/binned
    
    term1 = np.empty_like(error[:-1])
    term2 = np.empty_like(error[:-1])
    np.divide(pr_error[:-1], binned[:-1], out=term1, where=mask)
    np.square(term1, out=term1)
    np.divide(pr_error[1:], binned[1:], out=term2, where=mask)
    np.square(term2, out=term2)
    np.sqrt(term1 + term2, out=error[:-1], where=mask)
    error[-1] = pr_error[-1]/binned[-1]
"""