# atmospheric objects classes

import pandas as pd
from warnings import warn

class gas:
    def __init__(self, name, abun = '1', unit = 'scl') -> None:
        self.code = None
        self.abun = abun
        self.unit = unit
        if name == 'HDO':
            self.name = 'H2O'
            self.code = 'HIT[1:4]'
        else:
            self.name = name
            self.code = f'HIT[{self.get_HITRAN_code()}]'

    def __str__(self) -> str:
        return str([self.name, self.abun, self.unit, self.code])
    
    def get_HITRAN_code(self):
        if self.code is not None:
            return self.code
        else:
            tab = pd.read_csv('molecular_metadata.txt', sep = '\\s+')
            code = tab[tab.Formula == self.name]['Molecule_ID']
            if not code.empty:
                return code.iloc[0]
            else:
                warn(f'{self.name} is not a HITRAN molecule')
                return None
            
class aeros:
    def __init__(self, name, abun = '1', unit = 'scl', size = '1', sunit = 'scl', type='CRISM_Wolff') -> None:
        self.name = name
        self.abun = abun
        self.unit = unit
        self.size = size
        self.sunit = sunit
        self.type = type
    
    def __str__(self) -> str:
        return str([self.name, self.abun, self.unit, self.size, self.sunit, self.type])

class atmosphere:
    def __init__(self, glist=[], alist=[], clist=[]) -> None:
        self.gas_list = []
        for gg in glist:
            self.gas_list.append(gas(name=gg))

        self.aerosol_list = []
        for aa in alist:
            self.aerosol_list.append(aeros(name=aa))
        
        self.continuum_list = clist

    def get_atmosphere(self, cfg) -> None:
        if 'ATMOSPHERE-GAS' in cfg.keys():
            glist = cfg['ATMOSPHERE-GAS'].split(',')
            gunit = cfg['ATMOSPHERE-UNIT'].split(',')
            gabun = cfg['ATMOSPHERE-ABUN'].split(',')
            for gg,unit,abun in zip(glist,gunit,gabun):
                self.gas_list.append(gas(name=gg, abun=abun, unit=unit))

        if 'ATMOSPHERE-AEROS' in cfg.keys():
            alist = cfg['ATMOSPHERE-AEROS'].split(',')
            aunit = cfg['ATMOSPHERE-AUNIT'].split(',')
            aabun = cfg['ATMOSPHERE-AABUN'].split(',')
            asize = cfg['ATMOSPHERE-ASIZE'].split(',')
            asunit = cfg['ATMOSPHERE-ASUNI'].split(',')
            atype = cfg['ATMOSPHERE-ATYPE'].split(',')
            for aa,unit,abun,size,size_unit,type in zip(alist,aunit,aabun,asize,asunit,atype):
                self.aerosol_list.append(aeros(name=aa, abun=abun, unit=unit, size=size, sunit=size_unit,type=type))

        if 'ATMOSPHERE-CONTINUUM' in cfg.keys():
            self.continuum_list = cfg['ATMOSPHERE-CONTINUUM'].split(',')     
    
    def edit_cfg(self, cfg) -> None:
        gname = []
        gunit = []
        gabun = []
        gtype = []
        for gg in self.gas_list:
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
        for aer in self.aerosol_list:
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
        cfg['ATMOSPHERE-CONTINUUM'] = ','.join(self.continuum_list)

    def add_gas(self, gname, gabun='1', gunit='scl') -> None:
        gg = gas(gname, gabun, gunit)
        self.gas_list.append(gg)
    
    def add_aeros(self, aname, aabun='1', aunit='scl', size = '1', sunit='scl', type='CRISM_Wolff') -> None:
        aer = aeros(aname, aabun, aunit, size, sunit, type)
        self.aerosol_list.append(aer)
    
    def add_continuum(self, cont):
        self.continuum_list.append(cont)

    def remove_gas(self, gname):
        gg = gas(gname)
        self.gas_list.remove(gg)

    def remove_gas(self, aname):
        aer = gas(aname)
        self.aerosol_list.remove(aer)

    def add_continuum(self, cont):
        self.continuum_list.remove(cont)

    def reset_atmosphere(self) -> None:
        self.gas_list = []
        self.aerosol_list = []
        self.continuum_list = []