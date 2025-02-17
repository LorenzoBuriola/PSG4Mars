import numpy as np
import pypsg.cfg as cfg
from pypsg.run_psg import run_psg
from pypsg.utils import transform_date
import pypsg.atm_obj as atm

cfg_path = '/home/buriola/PSG/PSG4Mars/data/cfg/'
cfg_b = cfg.read_cfg(f'{cfg_path}basic_cfg.txt')

lat = 0.0
long = 0.0
date = '2019/12/23 00:00'

lyr_path = '/home/buriola/PSG/PSG4Mars/data/lyr/'
lyo_path = '/home/buriola/PSG/PSG4Mars/data/lyo/'
rad_path = '/home/buriola/PSG/PSG4Mars/data/rad/'
ranges = np.arange(100,3050,50)

stringfile = f"{'{:.0f}'.format(lat)}_{'{:.0f}'.format(long)}_{transform_date(date)}"
cfg.generate_profile(cfg_b, date, lat, long, f'{cfg_path}test_rad/')

cfg_ds = cfg.read_cfg(f'{cfg_path}test_rad/cfg_{stringfile}.txt')
atmos = atm.atmosphere()
atmos.get_atmosphere(cfg_ds)

atmos.continuum_list = ['Refraction', 'CIA_all', 'Layering', 'Contributions']
atmos.aerosol_list = []

atmos.edit_cfg(cfg_ds)

cfg_ds['SURFACE-EMISSIVITY'] = 1.
cfg_ds['SURFACE-ALBEDO'] = 0.
res = 1e-4
cfg_ds['GENERATOR-RESOLUTION'] = res

for i in range(len(ranges)-1):
    print(f'frequency: {ranges[i]}')
    cfg_ds['GENERATOR-RANGE1'] = ranges[i] + res
    cfg_ds['GENERATOR-RANGE2'] = ranges[i+1]
    cfg.dict_to_cfg(cfg_ds, f'{cfg_path}test_rad/cfg_{stringfile}_hr.txt')
    run_psg(cfg_file=f'{cfg_path}test_rad/cfg_{stringfile}_hr.txt', type='lyr', out_file=f"{lyr_path}test_rad/lyr_{stringfile}_freq{ranges[i]}_{ranges[i+1]}_hr.txt", verbose=False)
    run_psg(cfg_file=f'{cfg_path}test_rad/cfg_{stringfile}_hr.txt', type='lyo', out_file=f"{lyo_path}test_rad/lyo_{stringfile}_freq{ranges[i]}_{ranges[i+1]}_hr.txt", verbose=False)
    run_psg(cfg_file=f'{cfg_path}test_rad/cfg_{stringfile}_hr.txt', type='rad', out_file=f"{rad_path}test_rad/rad_{stringfile}_freq{ranges[i]}_{ranges[i+1]}_hr.txt", verbose=False)