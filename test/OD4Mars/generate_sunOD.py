import numpy as np
import PSGpy.cfg as cfg
from PSGpy.run_psg import run_psg

ranges = np.arange(90, 3010, 40)

cfg_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/sun_cfg.txt'
irrad_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/irrad_sun/'

cfg_dict = cfg.read_cfg(cfg_path)

for i in range(len(ranges)-1):
    cfg_dict['GENERATOR-RANGE1'] = ranges[i]
    cfg_dict['GENERATOR-RANGE2'] = ranges[i+1]-0.01
    cfg_dict['GENERATOR-RESOLUTION'] = 0.01
    cfg.dict_to_cfg(cfg_dict, 'cfg_temp.txt')
    run_psg('cfg_temp.txt', f'{irrad_path}sun_{ranges[i]}_{ranges[i+1]}.txt')
    break


