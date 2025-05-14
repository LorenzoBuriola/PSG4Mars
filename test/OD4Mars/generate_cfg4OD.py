import numpy as np
import pypsg.cfg as cfg
import pypsg.atm_obj as atm

def generate_OD_cfg(gas_list, ipath, opath, res = 1e-4):
    cfg_dict = cfg.read_cfg(f'{ipath}mean_cfg.txt')
    for g_name in gas_list:
        temp = cfg_dict.copy()
        atmos = atm.atmosphere()
        atmos.get_atmosphere(temp)
        atmos.add_gas(g_name)
        atmos.continuum_list = ['Refraction', 'Layering', 'Contributions']
        atmos.edit_cfg(temp)
        if g_name == 'H2O':
            temp['ATMOSPHERE-GAS'] = 'H2O,H2O,H2O,H2O'
            temp['ATMOSPHERE-UNIT'] = 'scl,scl,scl,scl'
            temp['ATMOSPHERE-ABUN'] = '1,1,1,1'
            temp['ATMOSPHERE-TYPE'] = 'HIT[1:1],HIT[1:2],HIT[1:3],HIT[1:5]'
            temp['ATMOSPHERE-NGAS'] = 4
        temp['GENERATOR-RESOLUTION'] = res
        cfg.dict_to_cfg(dictionary=temp,file_path=f'{opath}cfg_{g_name}.txt')

gas_list = ['CO2','CO','H2O','O3','HCl','HDO']

ipath = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/cfg/',
opath='/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/cfg/OD_gen/'

generate_OD_cfg(gas_list, ipath, opath)