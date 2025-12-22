import logging
import numpy as np
import xarray as xr
import subprocess

logger = logging.getLogger(__name__)

def input4pack(gas_list, ranges, degree, coeff_path, out_path):

    nn = int((ranges[-1]-ranges[0])/1e-2)
    vv = np.arange(ranges[0], ranges[-1], 1e-2)

    layers = 55

    for ii,gas in enumerate(gas_list):
        logger.info(f'Processing {gas}')
        coeff_list =[]
        for rr in ranges[:-1]:
            coeff = xr.open_dataset(f'{coeff_path}{gas}/coeff_{degree}_{gas}_freq{rr}_{int(rr+40)}.nc')
            coeff_list.append(coeff)
        coeff_all = xr.concat(coeff_list, dim='freq')
        coeff_all = coeff_all.sortby('freq')
        coeff_all = coeff_all.transpose('freq', 'altitude', 'degree')
        nquad = coeff_all.mask0.sum(dim = 'freq').values

        ind = []
        for jj in range(layers):
            ind.append(np.argwhere(coeff_all.mask0.values[:, jj]).flatten())

        cind = coeff_all.coeff.values

        for jj in range(layers):
            namefile = f'c{ii+1:02d}{jj+1:03d}'
            with open(f'{out_path}{namefile}', 'wb') as fid1:
                fid1.write(np.array(nn, dtype=np.int32).tobytes())
                fid1.write(np.array(nquad[jj], dtype=np.int32).tobytes())
                fid1.write(np.array(ind[jj]+1, dtype=np.int32).tobytes()) # Fortran indexing
                fid1.write(np.array(vv[ind[jj]], dtype=np.float32).tobytes())
                for kk in reversed(range(degree+1)):
                    fid1.write(np.array(cind[ind[jj],jj,kk], dtype=np.float32).tobytes())

def run_packoneband(exe_path, degree):
    cmd = ['./pack_oneband.out', degree]
    result = subprocess.run(cmd, cwd=exe_path,
                            capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f'Error running packoneband: {result.stderr}')
    else:
        logger.info(f'packoneband output: {result.stdout}')
