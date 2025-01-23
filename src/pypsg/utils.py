# utils

import numpy as np
import pandas as pd
from datetime import datetime
from scipy.constants import speed_of_light,Planck,Boltzmann

def read_out(file_path, to_DF = True):
    if to_DF is True:
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
        table = pd.read_csv(file_path, delimiter="\\s+", names=header, comment='#')
    else:
        table = np.loadtxt(file_path, delimiter=" ", comments='#')
    return table

def safe_log(x, eps=1e-323):
    result = np.where(x > eps, x, np.log(eps))     
    np.log(result, out=result, where=result > 0)     
    return result

def transform_date(date_str, format1 = '%Y/%m/%d %H:%M', format2 = '%Y%m%d-%H%M'):
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
    return aps + ps*1e-3*bps

def name_file(type, date, lat, lon):
    return f"{type}_{'{:.0f}'.format(lat)}_{'{:.0f}'.format(lon)}_{transform_date(date)}"