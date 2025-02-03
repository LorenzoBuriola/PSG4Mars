import numpy as np

def read_od_klima(filename):
    k = {}
    with open(filename, 'rb') as fid:
        k['filename'] = filename
        
        # Record 1
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['isigma'] = np.fromfile(fid, dtype=np.int32, count=1)[0]  # number of optical thickness points
        k['ngas'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['iband'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['freini'] = np.fromfile(fid, dtype=np.float64, count=1)[0]
        k['freend'] = np.fromfile(fid, dtype=np.float64, count=1)[0]
        k['frestep'] = np.fromfile(fid, dtype=np.float64, count=1)[0]
        k['pressure'] = np.fromfile(fid, dtype=np.float64, count=1)[0]  # pressure of the layer
        k['temperature'] = np.fromfile(fid, dtype=np.float64, count=1)[0]  # temperature of the layer
        k['raircol'] = np.fromfile(fid, dtype=np.float64, count=1)[0]  # air column of the layer
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        
        # Record 2
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['usedmol'] = []
        for i in range(k['ngas']):
            k['usedmol'].append(np.fromfile(fid, dtype='S1', count=7).tobytes().decode('utf-8'))  # molecules related to optical thickness
        
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        
        # Record 3
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['used_db'] = []
        for i in range(k['ngas']):
            k['used_db'].append(np.fromfile(fid, dtype='S1', count=40).tobytes().decode('utf-8'))  # molecules related to optical thickness
        
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        
        # Record 4
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['gas_column'] = np.fromfile(fid, dtype=np.float64, count=k['ngas'])  # molecules related to optical thickness
        
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        
        # Record 5
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['od'] = np.fromfile(fid, dtype=np.float64, count=k['isigma'])
        
        dum = np.fromfile(fid, dtype=np.int32, count=1)[0]
        k['v'] = np.linspace(k['freini'], k['freend'], k['isigma'])
    
    return k

