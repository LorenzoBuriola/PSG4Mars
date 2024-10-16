from pandas import read_csv
from warnings import warn

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
            tab = read_csv('molecular_metadata.txt', sep = '\s+')
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