import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

def find_nearest(array, value):
    aa = array[array < value]
    val = aa[np.argmax(aa)]
    return val

def fitted_line_plot(ds):
    xx = np.linspace(-60,60,120).reshape(-1,1)
    yy = ds.polyfit_coefficients.sel(degree = 3).values*xx**3 + ds.polyfit_coefficients.sel(degree = 2).values*xx**2 + ds.polyfit_coefficients.sel(degree = 1).values*xx+ds.coeffs_3.sel(degree = 0).values
    plt.errorbar(xx,yy, yerr=ß color = 'red', linestyle = '--', label = 'cubic fit', lw = 2)

def check_plot(gas, freq, alt, ods, pp):
    toplot = ods.sel(freq = freq, altitude = alt, method='nearest')
    print(f'Plotting freq {toplot.freq.values} and alt {toplot.altitude.values}')
    toplotpp = pp.sel(freq = freq, altitude = alt, method='nearest')
    od = toplot.od.values
    error = toplot.error.values
    DT = toplot.DeltaT.values
    plt.style.use('ggplot')
    plt.plot(DT, od, marker = 'x', markersize=7, lw=5, linestyle = ' ', label=f'simulated data', color = 'blue')
    plt.xlabel(r'$\Delta$T [K]', fontsize = 16)
    plt.ylabel(r'Optical Depth ($\tau$)', fontsize = 16)
    plt.title(f'gas = {gas}, ' + r'$\nu$ ' + f'= {freq}, h = {alt}', fontsize = 18)
    fitted_line_plot(toplotpp)
    plt.legend(fontsize = 16, facecolor = 'white')
    plt.show()
    
def plot_fit(gas, freq, alt):
    ranges = np.arange(90, 3050, 40)
    coeff_path = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/coeff/'
    od_path = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/od/'
    freq1 = find_nearest(ranges, freq) 
    freq2 = freq1 + 40
    ds = xr.open_dataset(f'{od_path}{gas}/od_{gas}_freq{freq1}_{freq2}.nc')
    pp = xr.open_dataset(f'{coeff_path}{gas}/coeff_{gas}_freq{freq1}_{freq2}.nc')     
    check_plot(gas, freq, alt, ds, pp)