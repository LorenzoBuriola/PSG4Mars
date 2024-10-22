# Lorenzo Buriola
# 21 ottobre 20224
# pypsg.py e' un insieme di funzioni e wrapper utili per lanciare psg da python notebook

import re
import json
import os
import numpy as np
import pandas as pd
import docker

from requests import post
from warnings import warn
from scipy.stats import binned_statistic
from datetime import datetime
from scipy.constants import speed_of_light,Planck,Boltzmann

########################################################################################################
# docker management functions

def is_container_running(name):
    RUNNING = "running"
    docker_client = docker.from_env()
    try:
        container = docker_client.containers.get(name)
    except docker.errors.NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == RUNNING

def start_container(name) -> None:
    docker_client = docker.from_env()
    docker_client.containers.get(name).start()

def stop_container(name) -> None:
    docker_client = docker.from_env()
    docker_client.containers.get(name).stop()

########################################################################################################
# run psg

def run_psg(cfg_file, out_file = 'temp.txt', 
            type = 'rad', wgeo = 'y', wephm = 'n', watm = 'n', whdr = 'y',
            local = True, verbose = True):
    """
    It runs PSG requesting to http

    Parameters
    ----------
    cfg_file: string - path of the configuration file
    type: string - type of output wanted, default is Radiance (rad)
    out_file: string - path of the output file
    local: boolean - if run psg locally or not, default is yes (not local run will raise a warning)
    verbose: boolean - if print details, default is yes
    """

    # Check if type selected exists
    type_list = ['rad', 'noi', 'trn', 'atm', 'str', 'tel', 'srf', 'cfg', 'ret', 'lyo', 'lyr', 'all']
    if type not in type_list:
        warn(f'{type} is not a known type, output file will be empty!')

    # Check for wgeo
    if wgeo not in ['y', 'n']:
        warn(f'{wgeo} is not a known type, output file will be empty!')
    
    #Check for wephm
    wephm_list = ['y', 'N', 'T', 'S', 'P', 'n']
    if wephm not in wephm_list:
        warn(f'{wephm} is not a known type, output file will be empty!')

    # Check for watm
    if watm not in ['y', 'n']:
        warn(f'{watm} is not a known type, output file will be empty!')
    
    # Check for watm
    if whdr not in ['y', 'n']:
        warn(f'{whdr} is not a known type, output file will be empty!')
        
    data = {
        'type': type,
        'wgeo' : wgeo,
        'wephm' : wephm,
        'watm' : watm,
        'whdr' : whdr,
        'file': open(cfg_file).read(),
    }
    if local == True:
        url = 'http://localhost:3000/api.php'
        #TODO if not is_container_running('psg'):
        #TODO   warn('container psg is not running, please start container')
    else:
        url = 'https://psg.gsfc.nasa.gov/api.php'
        warn('PSG is not running locally')
    response = post(url, data=data)                 # 'curl' command
    if verbose == True:
        print(f'PSG is running at {url}')
        print(f'type = {type}')
        print(f'Input file: {cfg_file}')
        print(f'Output file: {out_file}')
    with open(out_file, 'w') as ofile:
        ofile.write(response.text)                  # write to output file

########################################################################################################
# read, edit and write cfg files

def read_cfg(file_path):
    """
    It reads the configuration file
    
    Parameters
    ----------
    file_path: string - path of the configuration file

    Returns
    --------
    variables: dictionary - dictionary of all the variables in configuration file
    """
    # Dictionary to hold the parsed variables and their values
    variables = {}
    # Regular expression to match the pattern <name>value
    pattern = re.compile(r'<(.*?)>(.*)')
    # Read the file line by line
    with open(file_path, 'r') as file:
        for line in file:
            match = pattern.match(line.strip())
            if match:
                # Extract the variable name and value
                name, value = match.groups()
                variables[name] = value
    return variables

def cfg_to_json(file_path):
    """
    It reads the configuration file and writes it in a JSON format
    
    Parameters
    ----------
    file_path: string - path of the configuration file
    """
    # Using of the function read_cfg that read
    variables = read_cfg(file_path)        
    # Changing extension
    base_name,_ = os.path.splitext(file_path)   
    new_name = f'{base_name}.json'
    with open(new_name, 'w') as ofile:
        json.dump(variables,ofile)
    return

def dict_to_cfg(dictionary, file_path):
    """
    It writes a dictionary to a configuration file for PSG (.txt)

    Parameters
    ----------
    dd: dictionay - data to write
    file_path: string - path of the configuration file
    """
    with open(file_path, 'w') as ofile:
        for key in dictionary:
            ofile.write(f'<{key}>{dictionary[key]}\n')
    return

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
    cfg_dict['OBJECT-OBS-LONGITUDE'] = longitude
    dict_to_cfg(dictionary=cfg_dict, file_path='cfg_temp.txt')
    run_psg.run_psg(cfg_file='cfg_temp.txt',type='cfg', wephm = 'y', watm='y', 
                    out_file=f'{opath}cfg_{latitude}_{longitude}_{transform_date(date)}.txt', verbose=False)

########################################################################################################
# atmospheric objects classes

class gas:
    def __init__(self, name, abun, unit) -> None:
        self.name = name
        self.abun = abun
        self.unit = unit
        self.code = None
        self.code = f'HIT[{self.get_HITRAN_code()}]'
    
    def get_HITRAN_code(self):
        if self.code is not None:
            return self.code
        else:
            tab = pd.read_csv('molecular_metadata.txt', sep = '\s+')
            code = tab[tab.Formula == self.name]['Molecule_ID']
            if not code.empty:
                return code.iloc[0]
            else:
                warn(f'{self.name} is not a HITRAN molecule')
                return None
            
class aeros:
    def __init__(self, name, abun, unit, size, sunit, type) -> None:
        self.name = name
        self.abun = abun
        self.unit = unit
        self.size = size
        self.sunit = sunit
        self.type = type

class atmosphere:
    def __init__(self) -> None:
        self.g_obj_list = []
        self.a_obj_list = []
        self.clist = []

    def get_atmosphere(self, cfg) -> None:
        glist = cfg['ATMOSPHERE-GAS'].split(',')
        alist = cfg['ATMOSPHERE-AEROS'].split(',')
        self.clist = cfg['ATMOSPHERE-CONTINUUM'].split(',')
        gunit = cfg['ATMOSPHERE-UNIT'].split(',')
        gabun = cfg['ATMOSPHERE-ABUN'].split(',')
        ngas = float(cfg['ATMOSPHERE-NGAS'])
        #check
        if ngas!=len(glist):
            warn(f"Number of gas listed ['ATMOSPHERE-GAS'] ({len(glist)}) and varibale ['ATMOSPHERE-NGAS'] ({ngas}) are not equal")
            return(-1)
        aunit = cfg['ATMOSPHERE-AUNIT'].split(',')
        aabun = cfg['ATMOSPHERE-AABUN'].split(',')
        asize = cfg['ATMOSPHERE-ASIZE'].split(',')
        asunit = cfg['ATMOSPHERE-ASUNI'].split(',')
        atype = cfg['ATMOSPHERE-ATYPE'].split(',')
        naeros = float(cfg['ATMOSPHERE-NAERO'])
        # check
        if naeros!=len(alist):
            warn(f"Number of aerosol listed ['ATMOSPHERE-AEROS'] ({len(alist)}) and varibale ['ATMOSPHERE-NAERO'] ({naeros}) are not equal")
            return(-1)
        
        for gas,unit,abun in zip(glist,gunit,gabun):
            self.g_obj_list.append(gas(name=gas, abun=abun, unit=unit))

        for aeros,unit,abun,size,size_unit,type in zip(alist,aunit,aabun,asize,asunit,atype):
            self.a_obj_list.append(aeros(name=aeros, abun=abun, unit=unit, size=size, sunit=size_unit,type=type))
    
    def edit_cfg(self, cfg) -> None:
        gname = []
        gunit = []
        gabun = []
        gtype = []
        for gg in self.g_obj_list:
            gname.append(gg.name)
            gunit.append(gg.unit)
            gabun.append(gg.abun)
            gtype.append(gg.code)
        cfg['ATMOSPHERE-GAS'] = ','.join(gname)
        cfg['ATMOSPHERE-UNIT'] = ','.join(gunit)
        cfg['ATMOSPHERE-ABUN'] = ','.join(gabun)
        cfg['ATMOSPHERE-TYPE'] = ','.join(gtype)
        cfg['ATMOSPHERE-NGAS'] = len(gname)
        aname =[]
        aunit = []
        aabun = []
        asize = []
        asunit = []
        atype = []
        for aer in self.a_obj_list:
            aname.append(aer.name)
            aunit.append(aer.unit)
            aabun.append(aer.abun)
            asize.append(aer.size)
            asunit.append(aer.sunit)
            atype.append(aer.type)
        cfg['ATMOSPHERE-AEROS'] = ','.join(aname)
        cfg['ATMOSPHERE-AUNIT'] = ','.join(aunit)
        cfg['ATMOSPHERE-AABUN'] = ','.join(aabun)
        cfg['ATMOSPHERE-ASIZE'] = ','.join(asize)
        cfg['ATMOSPHERE-ASUNI'] = ','.join(asunit)
        cfg['ATMOSPHERE-NAERO'] = len(aname)
        cfg['ATMOSPHERE-ATYPE'] = ','.join(atype)
        #other
        cfg['ATMOSPHERE-CONTINUUM'] = ','.join(self.clist)

    def add_gas(self, gname, gabun=1, gunit='scl') -> None:
        gg = gas(gname, gabun, gunit)
        self.g_obj_list.append(gg)
    
    def add_aeros(self, aname, aabun=1, aunit='scl', size = 1, sunit='scl', type='CRISM_Wolff') -> None:
        aer = aeros(aname, aabun, aunit, size, sunit, type)
        self.a_obj_list.append(aer)
    
    def add_continuum(self, cont):
        self.clist.append(cont)

    def reset_atmosphere(self) -> None:
        self.g_obj_list = []
        self.a_obj_list = []
        self.clist = []

########################################################################################################
# OD compiutation and binning

def OD_compute(data):
    altitude = data.columns[1:].to_numpy(dtype=float)
    paths = np.diff(altitude).reshape(1,-1)
    df_out = data.iloc[:,:-1].copy()
    df_out.iloc[:,1:] = data.iloc[:,1:-1]*paths
    names = [f'level_{i+1}' for i in range(len(df_out.columns)-1)]
    names.insert(0,'freq')
    df_out.columns = names
    return df_out
    
def OD_binning(high_res, low_res):
    low_res.sort_values(by='freq',inplace=True)
    high_res.sort_values(by='freq',inplace=True)
    f_low = low_res.freq.to_numpy()
    dw = f_low[1]-f_low[0]
    edges = f_low-dw/2
    edges = np.append(edges,f_low[-1]+dw/2)
    f_high = high_res.freq.to_numpy()
    ods = high_res.to_numpy()[:,1:].T
    trn = np.exp(-ods)
    cum_trn = np.cumprod(trn[::-1,:], axis=0)[::-1,:]
    binned,_,_ = binned_statistic(x=f_high,values=cum_trn,statistic='mean',bins=edges)
    sec_binned,_,_ = binned_statistic(x=f_high,values=ods,statistic='mean',bins=edges)
    trn_bin = 0.7*sec_binned
    np.divide(binned[:-1],binned[1:], out=trn_bin[:-1], where=np.logical_and(binned[:-1]!=0, binned[1:]!=0))
    trn_bin[-1] = binned[-1]
    od_bin = trn_bin
    np.log(od_bin,out=od_bin,where=binned!=0)
    od_bin = np.where(binned!=0, -od_bin, od_bin)
    binned_df = pd.DataFrame(np.concatenate((f_low.reshape((-1,1)), od_bin.T), axis = 1), columns=low_res.columns)
    return binned_df

########################################################################################################
# utility functions

def read_out(file_path):
    # Read the lines in file
    with open(file_path) as ifile:
        bool = True
        line = None
        while bool:
            prevline = line
            line = ifile.readline()
            if not line.startswith('#'):
                bool = False

    # Last commented line is header
    header = prevline

    # Strip line and remove '#' 
    header = header[1:].strip().split()
    header = ['freq' if ee == 'Wave/freq' else ee for ee in header]

    df = pd.read_csv(file_path, delimiter="\s+", names=header, comment='#')
    return df

def safe_log(x, eps=1e-323):
    result = np.where(x > eps, x, np.log(eps))     
    np.log(result, out=result, where=result > 0)     
    return result

def transform_date(date_str, format1 = '%Y/%m/%d %H:%M', format2 = '%Y-%m-%d--%H-%M'):
    date = datetime.strptime(date_str, format1)
    new_format_date = datetime.strftime(date, format2)
    return new_format_date

def BlackBody(nu,T):
    h = Planck
    c = speed_of_light
    k = Boltzmann
    c1 = 2*h*c**2*10**8
    c2 = h*c/k*100
    return c1*nu**3/(np.exp(c2*nu/T)-1)

def generate_pressure_levels(ps):
    tab = pd.read_csv('aps_bps.txt')
    aps = tab.aps.to_numpy()*1e-5
    bps = tab.bps.to_numpy()
    return aps + ps*bps

def vez_bin(high_res, low_res):
    low_res.sort_values(by='freq',inplace=True)
    high_res.sort_values(by='freq',inplace=True)
    f_low = low_res.freq.to_numpy()
    dw = f_low[1]-f_low[0]
    f_high = high_res.freq.to_numpy()
    ods = high_res.to_numpy()[:,1:].T
    trn = np.exp(-ods)
    cum_trn = np.cumprod(trn[::-1,:], axis=0)

    ll = ods.shape[0]
    vv = len(f_low)
    c_tr = cum_trn[::-1,:]

    tt = np.ones((ll+1, vv))
    odt = np.zeros((ll, vv))

    for i in reversed(range(ll)):
        for j in range(vv):
            ind = np.nonzero(np.abs(f_high-f_low[j])<=dw)
            buff = np.mean(ods[i, ind])
            buf = np.mean(c_tr[i,ind])/tt[i+1,j]
            if buf > 0:
                odt[i,j] = -np.log(buf)
            else:
                odt[i,j] = 0.7*buff
            tt[i,j] = np.exp(-odt[i,j])*tt[i+1,j]

    binned_df = pd.DataFrame(np.concatenate((f_low.reshape((-1,1)), odt.T), axis = 1), columns=low_res.columns)

    return binned_df
