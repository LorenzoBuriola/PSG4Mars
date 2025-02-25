import numpy as np
import pandas as pd
import pypsg.cfg as cfg
import pypsg.atm_obj as atm
from pypsg.run_psg import run_psg
from pypsg.utils import name_file

def generate_profiles(latitudes, longitudes, dates, opath, ipath=None) -> None:
    dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()
    cfg_df = cfg.read_cfg(f'{ipath}basic_cfg.txt')
    for date in dates_list:
        for lat in latitudes:
            for long in longitudes:
                cfg.generate_profile(cfg_df, date, lat, long, opath=opath)

def custom_edges(aa, nbin) -> None:
    nn = len(aa)
    return np.interp(np.linspace(0, nn, nbin + 1),
                     np.arange(nn),
                     np.sort(aa))

def generate_p_levels(latitudes, longitudes, dates, ipath, ofile = 'p_edges.npy'):
    dates_list = dates.strftime('%Y/%m/%d %H:%M').to_list()
    p = []
    for date in dates_list:
        for lat in latitudes:
            for long in longitudes:
                temp_cfg = cfg.read_cfg(f"{ipath}{name_file('cfg', date, lat, long)}.txt")
                temp_df = cfg.read_atm_layers(temp_cfg)
                p.append(temp_df.Pressure)
    p = np.asarray(p)
    pcut1 = 1e-8
    pcut2 = 1e-3
    pmin = p.min()
    p_med = p[np.logical_and(p>pcut1,p<pcut2)]
    e_med = custom_edges(p_med, 20)
    e_med = e_med[1:-1]
    p_high = p[p>=pcut2]
    e_high = custom_edges(p_high,30)
    ee = np.concatenate([[pmin,pcut1],e_med,e_high])
    if ofile is not None:
        np.save(ofile, ee)
    return ee

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

    df = pd.DataFrame({
        'Pressure' : p_edges,
        'Temperature' : meanT,
        'CO2' : meanCO2,
        'CO' : meanCO,
        'H2O' : meanH2O,
        'O3' : meanO3
    })
    df = df.loc[::-1].reset_index(drop=True)
    #df.loc[0,'H2O'] = df.loc[2,'H2O']
    #df.loc[1,'H2O'] = df.loc[2,'H2O']

    df['HCl'] = 1e-9

    if ofile is not None:
        df.to_csv('mean_profile.csv', index=False, float_format='%.4e')
    return df

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

def T_shift(DT, cfg_df):
    cfg_out = cfg_df.copy()
    df = cfg.read_atm_layers(cfg_df)
    df.Temperature = df.Temperature+DT
    cfg.write_atm_layers(df,cfg_out)
    cfg_out['SURFACE-TEMPERATURE'] = df.loc[0,'Temperature']
    return cfg_out

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
                
    
    