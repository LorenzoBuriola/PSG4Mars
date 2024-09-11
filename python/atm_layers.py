import numpy as np
import pandas as pd

import cfg_io
import run_psg
from utils import transform_date

def read_atm_layers(cfg_dict):
    n_layer = int(cfg_dict['ATMOSPHERE-LAYERS'])
    names = 'Pressure,Temperature,'+cfg_dict['ATMOSPHERE-LAYERS-MOLECULES']
    names = names.split(',')
    tab = np.zeros((n_layer, len(names)))
    for i in range(n_layer):
        tab[i,:] = np.fromstring(cfg_dict[f'ATMOSPHERE-LAYER-{i+1}'],sep=',')
    tab_df = pd.DataFrame(tab, columns=names)

    #TODO aggiungere trattazione dell'unita di misura

    return tab_df

def generate_profile(cfg_dict, date, latitude, longitude, opath) -> None:
    cfg_dict['OBJECT-DATE'] = date
    cfg_dict['OBJECT-OBS-LATITUDE'] = latitude
    cfg_dict['OBJECT-OBS-LATITUDE'] = longitude
    cfg_io.dict_to_cfg(dictionary=cfg_dict, file_path='cfg_temp.txt')
    run_psg.run_psg(cfg_file='cfg_temp.txt',type='cfg', wephm = 'y', watm='y', 
                    out_file=f'{opath}cfg_{latitude}_{longitude}_{transform_date(date)}.txt', verbose=False)
