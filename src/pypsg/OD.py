# OD compiutation and binning

import numpy as np
import pandas as pd
from scipy.stats import binned_statistic

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

"""
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
            ind = np.nonzero(np.abs(f_high-f_low[j])<=dw/2)
            buff = np.mean(ods[i, ind])
            buf = np.mean(c_tr[i,ind])/tt[i+1,j]
            if buf > 0:
                odt[i,j] = -np.log(buf)
            else:
                odt[i,j] = 0.7*buff
            tt[i,j] = np.exp(-odt[i,j])*tt[i+1,j]

    binned_df = pd.DataFrame(np.concatenate((f_low.reshape((-1,1)), odt.T), axis = 1), columns=low_res.columns)

    return binned_df
"""