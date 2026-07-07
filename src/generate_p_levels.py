import logging
import numpy as np
import pandas as pd
import PSGpy.cfg as cfg
from PSGpy.utils import name_file

logger = logging.getLogger(__name__)

def custom_edges(aa, pcut1, pcut2, n1, n2, n3):
    low  = aa[aa < pcut2]
    mid  = aa[(aa >= pcut2) & (aa <= pcut1)]
    high = aa[aa > pcut1]

    e_low = np.quantile(low, np.linspace(0, 1, n1 + 1))
    e_mid = np.quantile(mid, np.linspace(0, 1, n2 + 1))
    e_high = np.quantile(high, np.linspace(0, 1, n3 + 1))

    # Force the boundaries
    e_low[-1] = pcut2
    e_mid[0] = pcut2
    e_mid[-1] = pcut1
    e_high[0] = pcut1

    # Join without duplicating boundaries
    edges = np.unique(np.concatenate([
        e_low,
        e_mid[1:],
        e_high[1:]
    ]))
    return edges

def generate_p_levels(grid, p_filename, ofile):
    logger.info("Generating pressure levels...")
    dates_list = grid.dates.strftime('%Y/%m/%d %H:%M').to_list()
    p = []
    for date in dates_list:
        for lat in grid.latitudes:
            longs_to_use = [0] if abs(lat) == 90 else grid.longitudes
            for long in longs_to_use:
                temp_cfg = cfg.read_cfg(f"{p_filename}{name_file('cfg', date, lat, long)}.cfg")
                temp_df = cfg.read_atm_layers(temp_cfg)
                p.append(temp_df.Pressure)
    p = np.asarray(p)
    pcut2 = 1e-8
    pcut1 = 1e-3
    ee = custom_edges(p.flatten(), pcut1, pcut2, 5, 20, 30)
    
    logger.info('******************************')
    logger.info(f"Pressure levels generated:")
    for i in range(len(ee)):
        logger.info(f"Level {i+1}:\t{ee[i]:.3}")

    np.save(ofile, ee)
    logger.info("Pressure level generation completed.")

    return ee
