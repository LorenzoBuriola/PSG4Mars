import numpy as np
import pypsg.cfg as cfg
from pypsg.run_psg import run_psg

def T_shift(DT, cfg_df):
    cfg_out = cfg_df.copy()
    df = cfg.read_atm_layers(cfg_df)
    df.Temperature = df.Temperature+DT
    cfg.write_atm_layers(df,cfg_out)
    cfg_out['SURFACE-TEMPERATURE'] = df.loc[0,'Temperature']
    return cfg_out

gas_list = ['CO2', 'H2O', 'CO', 'O3', 'HCl', 'HDO']
cfg_path = '/home/buriola/PSG/PSG4Mars/data/cfg/'
lyo_path = '/home/buriola/PSG/PSG4Mars/data/lyo/'
lyr_path = '/home/buriola/PSG/PSG4Mars/data/lyr/'

ranges = np.arange(100,3050,50)
DTs = np.arange(-60, 70, 10)

print('Starting computing ODs\n')

for g_name in gas_list:
    print(f'Gas: {g_name}')
    cfg_dict = cfg.read_cfg(f'{cfg_path}/OD_gen/cfg_{g_name}.txt')
    for DT in DTs:
        print(f'Temperature shift: {DT}')
        temp = T_shift(DT, cfg_dict)
        for i in range(len(ranges)-1):
            temp['GENERATOR-RANGE1'] = ranges[i]
            temp['GENERATOR-RANGE2'] = ranges[i+1]
            print(f'freqs: {ranges[i]}-{ranges[i+1]}')
            cfg.dict_to_cfg(temp, f'{cfg_path}/OD_gen/cfg_temp.txt')
            run_psg(cfg_file=f'{cfg_path}/OD_gen/cfg_temp.txt',
                        type='lyo',
                        out_file=f"{lyo_path}{g_name}/lyo_{g_name}_{DT}_freq{ranges[i]}_{ranges[i+1]}.txt",
                        verbose=False)
            run_psg(cfg_file=f'{cfg_path}/OD_gen/cfg_temp.txt',
                        type='lyr',
                        out_file=f"{lyr_path}{g_name}/lyr_{g_name}_{DT}_freq{ranges[i]}_{ranges[i+1]}.txt",
                        verbose=False)

print("\nThat's all!")