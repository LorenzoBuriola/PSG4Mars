import logging
from pathlib import Path
import numpy as np
import PSGpy.cfg as cfg
from PSGpy.run_psg import run_psg

logger = logging.getLogger(__name__)
            
def T_shift(DT, cfg_df):
    cfg_out = cfg_df.copy()
    df = cfg.read_atm_layers(cfg_df)
    df['Temperature'] = (df['Temperature']+DT).round(1)
    cfg.write_atm_layers(df,cfg_out)
    cfg_out['SURFACE-TEMPERATURE'] = float(cfg_df['SURFACE-TEMPERATURE']) + DT
    return cfg_out

def generate_OD(gas_list, ranges, res, temperatures, cfg_path, lyo_path, lyr_path):
    cfg_path = Path(cfg_path)
    lyo_path = Path(lyo_path)
    lyr_path = Path(lyr_path)

    logger.info('Starting computing ODs\n')

    for g_name in gas_list:
        logger.info(f'Gas: {g_name}')
        cfg_dict = cfg.read_cfg(str(cfg_path / 'OD_gen' / f'cfg_{g_name}.txt'))
        for DT in temperatures:
            logger.info(f'Temperature shift: {DT}')
            temp = T_shift(DT, cfg_dict)
            for i in range(len(ranges)-1):
                logger.info(f'freqs: {ranges[i]}-{ranges[i+1]}')
                temp['GENERATOR-RANGE1'] = "{:.4f}".format(ranges[i])
                temp['GENERATOR-RANGE2'] = "{:.4f}".format(ranges[i+1])
                temp['GENERATOR-RESOLUTION'] = res
                temp_cfg = cfg_path / 'OD_gen' / 'cfg_temp.txt'
                cfg.dict_to_cfg(temp, str(temp_cfg))
                run_psg(cfg_file=str(temp_cfg),
                            kind='lyo',
                            wephm='y',
                            out_file=lyo_path / g_name / f"lyo_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}_{res:.0e}.txt",
                            verbose=False)
                run_psg(cfg_file=str(temp_cfg),
                            kind='lyr',
                            wephm='y',
                            out_file=lyr_path / g_name / f"lyr_{g_name}_{DT}_freq{ranges[i]:.0f}_{ranges[i+1]:.0f}_{res:.0e}.txt",
                            verbose=False)
    logger.info("OD generation completed")