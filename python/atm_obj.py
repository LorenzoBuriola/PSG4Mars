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
    def __init__(self, name, abun, size, unit) -> None:
        self.name = name
        self.abun = abun
        self.size = size
        self.unit = unit