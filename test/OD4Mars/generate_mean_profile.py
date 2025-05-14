import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pypsg.cfg as cfg
import pypsg.atm_obj as atm
from pypsg.utils import name_file

def generate_mean_profiles(latitudes, longitudes, dates, ipath, p_filename = 'p_edges.npy', ofile = None):
    dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()
    tt = []
    h2o = []
    co = []
    co2 = []
    o3 = []

    p_edges = np.load(p_filename)

    for date in dates_list:
        for lat in latitudes:
            for long in longitudes:
                temp_cfg = cfg.read_cfg(f"{ipath}{name_file('cfg', date, lat, long)}.txt")
                temp_df = cfg.read_atm_layers(temp_cfg)
                P = temp_df.Pressure.to_numpy()
                T = temp_df.Temperature.to_numpy()
                Water = temp_df.H2O.to_numpy()
                Monoxide = temp_df.CO.to_numpy()
                Dioxide = temp_df.CO2.to_numpy()
                Ozone = temp_df.O3.to_numpy()
                tt.append(np.interp(p_edges,P[::-1],T[::-1], right=np.nan))
                h2o.append(np.interp(p_edges,P[::-1],Water[::-1], right=np.nan))
                co.append(np.interp(p_edges,P[::-1],Monoxide[::-1], right=np.nan))
                co2.append(np.interp(p_edges,P[::-1],Dioxide[::-1], right=np.nan))
                o3.append(np.interp(p_edges,P[::-1],Ozone[::-1], right=np.nan))
    
    meanT = np.nanmean(tt, axis=0)
    meanCO2 = np.nanmean(co2, axis=0)
    meanCO = np.nanmean(co, axis=0)
    meanH2O = np.nanmean(h2o, axis=0)
    meanO3 = np.nanmean(o3, axis=0)

    stdT = np.nanstd(tt, axis=0)
    stdCO2 = np.nanstd(co2, axis=0)
    stdCO = np.nanstd(co, axis=0)
    stdH2O = np.nanstd(h2o, axis=0)
    stdO3 = np.nanstd(o3, axis=0)

    df_mean = pd.DataFrame({
        'Pressure' : p_edges,
        'Temperature' : meanT,
        'CO2' : meanCO2,
        'CO' : meanCO,
        'H2O' : meanH2O,
        'O3' : meanO3
    })
    df_mean = df_mean.loc[::-1].reset_index(drop=True)
    df_mean['HCl'] = 1e-9

    df_std = pd.DataFrame({
        'Pressure' : p_edges,
        'Temperature' : stdT,
        'CO2' : stdCO2,
        'CO' : stdCO,
        'H2O' : stdH2O,
        'O3' : stdO3
    })
    df_std = df_std.loc[::-1].reset_index(drop=True)

    if ofile is not None:
        df_mean.to_csv('mean_profile.csv', index=False, float_format='%.4e')

    return df_mean,df_std

def write_mean_cfg(df_prof, opath, ofile = 'mean_cfg.txt') -> None:
    if isinstance(df_prof, str):
        atm = pd.read_csv(df_prof, header=0)
    else:
        atm = df_prof
    cfg_df = {}
    cfg_df['OBJECT'] = 'Planet'
    cfg_df['OBJECT-NAME'] = 'Mars'
    cfg_df['GEOMETRY-REF'] = 'User'
    cfg_df['GEOMETRY'] = 'Nadir'
    cfg_df['GEOMETRY-OBS-ALTITUDE'] = '400.0'
    cfg_df['GEOMETRY-OBS-ANGLE'] = '0.0'
    cfg_df['GEOMETRY-ALTITUDE-UNIT'] = 'km'
    cfg_df['GENERATOR-INSTRUMENT'] = 'user'
    cfg_df['GENERATOR-GAS-MODEL'] = 'Y'
    cfg_df['GENERATOR-CONT-MODEL'] = 'Y'
    cfg_df['GENERATOR-CONT-STELLAR'] = 'N'
    cfg_df['GENERATOR-RANGEUNIT'] = 'cm'
    cfg_df['GENERATOR-RESOLUTIONUNIT'] = 'cm'
    cfg_df['GENERATOR-RESOLUTIONKERNEL'] = 'N'
    cfg_df['GENERATOR-RADUNITS'] = 'Wsrm2cm'
    cfg_df['GENERATOR-NOISE'] = 'NO'
    cfg_df['ATMOSPHERE-STRUCTURE'] = 'Equilibrium'
    cfg_df['ATMOSPHERE-PUNIT'] = 'bar'
    cfg_df['SURFACE-MODEL'] = 'Lambert'
    cfg_df['SURFACE-PHASEMODEL'] = 'ISO'
    cfg_df['SURFACE-ALBEDO'] = '0.0'
    cfg_df['SURFACE-EMISSIVITY'] = '1.0'
    cfg_df['SURFACE-NSURF'] = '0'
    n_layer = atm.shape[0]
    cfg_df['ATMOSPHERE-LAYERS'] = n_layer
    names = atm.columns
    cfg_df['ATMOSPHERE-LAYERS-MOLECULES'] = ",".join(names[2:])
    for i in range(n_layer):
        cfg_df[f'ATMOSPHERE-LAYER-{i+1}'] = ','.join('{:.4e}'.format(n) for n in atm.iloc[i,:].to_list())
    cfg_df['ATMOSPHERE-PRESSURE'] = atm.loc[0,'Pressure']
    cfg_df['SURFACE-TEMPERATURE'] = atm.loc[0,'Temperature']
    cfg.dict_to_cfg(cfg_df, f'{opath}{ofile}')

#INPUTS
latitudes = np.linspace(-90, 90, 49)
longitudes = np.linspace(0, 360, 65)[:-1]

start_date = '2019-03-24'
end_date = '2021-02-08'
dates = pd.date_range(
    start=start_date,
    end=end_date,
    periods=24,
    unit='s'
)

ipath = '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/profiles/'

data, std = generate_mean_profiles(latitudes, longitudes, dates, ipath, p_filename = 'p_edges.npy', ofile = None)
write_mean_cfg(data, '/home/buriola/PSG/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/', ofile = 'mean_cfg.txt')

#plots
T = data.Temperature.to_numpy()
P = data.Pressure.to_numpy()
sdT = std.Temperature.to_numpy()

fig,ax = plt.subplots()
ax.set_yscale('log')
ax.plot(T, P, color = 'black', marker='o')
ax.fill_betweenx(P, T-2*sdT, T+2*sdT, color = 'grey', alpha = 0.5)
ax.invert_yaxis()
ax.set_xlabel('T [K]')
ax.set_ylabel('P [bar]')

listnames = ['H2O', 'CO', 'CO2', 'O3']
fig2,ax2 = plt.subplots()
for i,obj in enumerate(listnames):
    mean = data[obj].to_numpy()
    sd = std[obj].to_numpy()
    fig,ax = plt.subplots()
    ax.plot(mean, P, color = 'black')
    ax.fill_betweenx(P, np.maximum(mean-2*sd,0), mean+2*sd, color = 'grey', alpha = 0.5)
    ax.invert_yaxis()
    ax.set_yscale('log')
    ax.set_ylabel('P [bar]')
    ax.set_xlabel(f'{obj} VMR')
    ax2.plot(mean, P, label=listnames[i])
ax2.invert_yaxis()
ax2.set_yscale('log')
ax2.set_ylabel('P [bar]')
ax2.set_xlabel('VMR')
ax2.set_xscale('log')
ax2.legend()
plt.show()