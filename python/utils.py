import pandas as pd
import numpy as np
from datetime import datetime

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