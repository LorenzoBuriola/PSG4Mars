import numpy as np
import pandas as pd
from scipy.stats import binned_statistic

def OD_compute(data):
    altitude = data.columns[1:].to_numpy(dtype=float)
    paths = np.diff(altitude).reshape(1,-1)
    df_out = data.iloc[:,:-1].copy()
    df_out.iloc[:,1:] = data.iloc[:,1:-1]*paths
    names = [f'level_{i}' for i in range(len(df_out.columns)-1)]
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
    ods = np.exp(-ods)
    binned,_,_ = binned_statistic(x=f_high,values=ods,statistic='mean',bins=edges)
    binned = -safe_log(binned)
    binned_df = pd.DataFrame(np.concatenate((f_low.reshape((-1,1)), binned.T), axis = 1), columns=low_res.columns)
    return binned_df
    
def safe_log(x, eps=1e-323):
    result = np.where(x > eps, x, np.log(eps))     
    np.log(result, out=result, where=result > 0)     
    return result