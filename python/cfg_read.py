import numpy as np
import pandas as pd

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