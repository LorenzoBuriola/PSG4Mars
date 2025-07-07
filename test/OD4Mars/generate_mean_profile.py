import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import PSGpy.cfg as cfg
import PSGpy.atm_obj as atm
from PSGpy.utils import name_file

def generate_mean_profiles(latitudes, longitudes, dates, ipath, p_filename = 'p_edges.npy', ofile = None,
                           verbose = True):
    dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()
    tt = []
    h2o = []
    co = []
    co2 = []
    o3 = []

    if verbose:
        print('Reading pressure edges from file...')
    p_edges = np.load(p_filename)
    if verbose:
        print(f'Number of pressure edges: {len(p_edges)}')

    if verbose:
        print('Reading profiles from cfg files and interpolating to pressure edges...')
    for date in dates_list:
        for lat in latitudes:
            for long in longitudes:
                temp_cfg = cfg.read_cfg(f"{ipath}{name_file('cfg', date, lat, long)}.txt")
                temp_df = cfg.read_atm_layers(temp_cfg)[::-1]  # Reverse the order to match pressure edges
                P = temp_df.Pressure.to_numpy()
                T = temp_df.Temperature.to_numpy()
                Water = temp_df.H2O.to_numpy()
                Monoxide = temp_df.CO.to_numpy()
                Dioxide = temp_df.CO2.to_numpy()
                Ozone = temp_df.O3.to_numpy()
                tt.append(np.interp(p_edges,P,T, right=np.nan))
                h2o.append(np.interp(p_edges,P,Water, right=np.nan))
                co.append(np.interp(p_edges,P,Monoxide, right=np.nan))
                co2.append(np.interp(p_edges,P,Dioxide, right=np.nan))
                o3.append(np.interp(p_edges,P,Ozone, right=np.nan))
    
    if verbose:
        print('Calculating mean and standard deviation for each pressure level...')
    meanT = np.nanmean(tt, axis=0)[::-1]
    meanCO2 = np.nanmean(co2, axis=0)[::-1]
    meanCO = np.nanmean(co, axis=0)[::-1]
    meanH2O = np.nanmean(h2o, axis=0)[::-1]
    meanO3 = np.nanmean(o3, axis=0)[::-1]

    stdT = np.nanstd(tt, axis=0)[::-1]
    stdCO2 = np.nanstd(co2, axis=0)[::-1]
    stdCO = np.nanstd(co, axis=0)[::-1]
    stdH2O = np.nanstd(h2o, axis=0)[::-1]
    stdO3 = np.nanstd(o3, axis=0)[::-1]

    p_edges = p_edges[::-1]  # Reverse the order to compute altitude correctly
    #Altitude
    print('Calculating altitude from pressure edges...')
    W_air = 43.65   #Weight [g/mol]
    R = 8314.46261815324  #Universal gas constant [mJ/(mol*K)]
    g_surf = 3.73     #Gravity [m/s^2]
    R_surf = 6779.8/2*1000  #Mars radius [m]

    hh = np.zeros_like(p_edges)

    print(f'Altitude at level 1: {hh[0]/1000} km')

    for i in range(len(p_edges)-1):
        g = g_surf*((hh[i]+R_surf)/ R_surf)**2
        H = R * meanT[i] / (W_air * g)  #Scale height [m]
        hh[i+1] = hh[i] + H * np.log(p_edges[i] / p_edges[i+1])  #Altitude [m]
        print(f'Altitude at level {i+2}:\t{hh[i+1]/1000} km')

    df_mean = pd.DataFrame({
        'Pressure' : p_edges,
        'Temperature' : meanT,
        'Altitude' : hh/1000,  # Convert to km
        'CO2' : meanCO2,
        'CO' : meanCO,
        'H2O' : meanH2O,
        'O3' : meanO3
    })
    df_mean['HCl'] = 1e-9

    df_std = pd.DataFrame({
        'Pressure' : p_edges,
        'Temperature' : stdT,
        'CO2' : stdCO2,
        'CO' : stdCO,
        'H2O' : stdH2O,
        'O3' : stdO3
    })

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
    cfg_df['OBJECT-GRAVITY'] = '3.73'
    cfg_df['OBJECT-GRAVITY-UNIT'] = 'g'
    cfg_df['OBJECT-DIAMETER'] = '6779.80'
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
    cfg_df['ATMOSPHERE-WEIGHT'] = '43.64'  # Weight of air [g/mol]
    cfg_df['ATMOSPHERE-LAYERS'] = n_layer - 1  # Number of layers (excluding the surface layer)
    names = atm.columns
    cfg_df['ATMOSPHERE-LAYERS-MOLECULES'] = ",".join(names[2:])
    for i in range(n_layer-1):
        cfg_df[f'ATMOSPHERE-LAYER-{i+1}'] = ','.join('{:.3e}'.format(n) for n in atm.iloc[i+1,:].to_list())
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

ipath = '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/profiles/'

data, std = generate_mean_profiles(latitudes, longitudes, dates, ipath, p_filename = 'p_edges.npy', ofile = None)
write_mean_cfg(data, '/home/buriola/Mars/PSG4Mars/NO_BACKUP/data/OD4Mars/cfg/', ofile = 'mean_cfg.txt')

#plots
T = data.Temperature.to_numpy()
P = data.Pressure.to_numpy()
hh = data.Altitude.to_numpy()  # Altitude in km
sdT = std.Temperature.to_numpy()

fig,ax = plt.subplots(figsize=(8, 6))
ax.set_yscale('log')
ax.plot(T, P, color = 'firebrick', marker='o', label='Mean T profile')
ax.plot(T+60, P, color = 'firebrick', linestyle='--', label=r'Mean T profile $\pm$ 60 K')
ax.plot(T-60, P, color = 'firebrick', linestyle='--')
ax.fill_betweenx(P, T-2*sdT, T+2*sdT, color = 'indianred', alpha = 0.5, label=r'2$\sigma$')
ax.invert_yaxis()
ax.set_xlabel('T [K]', fontsize=20)
ax.set_ylabel('P [bar]', fontsize=20)
ax.legend(fontsize = 14)
plt.tick_params(axis='both', which='major', labelsize=18)
ax_h = ax.twinx()
ax_h.plot(T, hh, alpha = 0)
ax_h.set_ylabel('Altitude [km]', fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=18)

fig.savefig('T_prof.png', dpi=300, bbox_inches='tight')

listnames = ['H2O', 'CO', 'CO2', 'O3']
fig2,ax2 = plt.subplots(figsize=(8, 6))
cc = ['blue', 'green', 'red', 'orange']
for i,obj in enumerate(listnames):
    mean = data[obj].to_numpy()
    sd = std[obj].to_numpy()
    fig,ax = plt.subplots()
    ax.plot(mean, P, color = 'darkorange', marker='o', label=listnames[i])
    ax.fill_betweenx(P, np.maximum(mean-2*sd,0), mean+2*sd, color = 'navajowhite', alpha = 0.5)
    ax.invert_yaxis()
    ax.set_yscale('log')
    ax.set_ylabel('P [bar]')
    ax.set_xlabel(f'{obj} VMR')
    fig.savefig(f'{obj}_profiles.png', dpi=300, bbox_inches='tight')
    ax2.plot(mean, P, label=listnames[i], color = cc[i], marker='.')
plt.close(fig)
ax2.plot(data['HCl'], P, label='HCl', color = 'purple', marker='.')
ax2.invert_yaxis()
ax2.set_yscale('log')
ax2.set_ylabel('P [bar]', fontsize=20)
ax2.set_xlabel('VMR', fontsize=20)
ax2.set_xscale('log')
ax2.legend(fontsize=16)
ax2.tick_params(axis='both', which='major', labelsize=18)
fig2.savefig('mean_profiles.png', dpi=300, bbox_inches='tight')