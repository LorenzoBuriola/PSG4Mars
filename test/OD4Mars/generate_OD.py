import numpy as np
import PSGpy.cfg as cfg
from PSGpy.run_psg import run_psg
import os

def check(path, value):
    if os.path.exists(path):
        with open(path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1]
            vv = float(last_line.split()[0])
            bb = np.isclose(vv,value, atol=1e-5, rtol=0)
            if bb == False:
                print(f'Mismatch: last freq is {vv}, expected {value}')
            else:
                print('OK')
    else:
        return -1
            

def T_shift(DT, cfg_df):
    cfg_out = cfg_df.copy()
    df = cfg.read_atm_layers(cfg_df)
    df.Temperature = df.Temperature+DT
    cfg.write_atm_layers(df,cfg_out)
    cfg_out['SURFACE-TEMPERATURE'] = float(cfg_df['SURFACE-TEMPERATURE']) + DT
    return cfg_out

gas_list = ['CO2'] #,'H2O', 'CO', 'O3', 'HCl', 'HDO']
cfg_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/'
lyo_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/lyo/'
lyr_path = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/lyr/'

ranges = np.arange(89.995, 3049.995, 40)
ranges = np.arange(609.995, 849.995, 40)
DTs = np.arange(-60, 70, 10)

print('Starting computing ODs\n')

for g_name in gas_list:
    print(f'Gas: {g_name}')
    cfg_dict = cfg.read_cfg(f'{cfg_path}OD_gen/cfg_{g_name}.txt')
    for DT in DTs:
        print(f'Temperature shift: {DT}')
        temp = T_shift(DT, cfg_dict)
        for i in range(len(ranges)-1):
            temp['GENERATOR-RANGE1'] = "{:.4f}".format(ranges[i])
            temp['GENERATOR-RANGE2'] = "{:.4f}".format(ranges[i+1])
            print(f'freqs: {ranges[i]}-{ranges[i+1]}')
            pp = f"{lyo_path}{g_name}/lyo_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}.txt"

            cfg.dict_to_cfg(temp, f'{cfg_path}OD_gen/cfg_temp.txt')
            run_psg(cfg_file=f'{cfg_path}OD_gen/cfg_temp.txt',
                        type='lyo',
                        out_file=f"{lyo_path}{g_name}/lyo_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}.txt",
                        verbose=False)
            run_psg(cfg_file=f'{cfg_path}OD_gen/cfg_temp.txt',
                        type='lyr',
                        out_file=f"{lyr_path}{g_name}/lyr_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}.txt",
                        verbose=False)
            bb = check(pp,ranges[i])
print("\nThat's all!")