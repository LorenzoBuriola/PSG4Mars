import pandas as pd

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
