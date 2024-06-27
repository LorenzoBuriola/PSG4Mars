import pandas as pd

def read_rad(file_path):
    # Read the lines in file
    with open(file_path) as ifile:
        lines = ifile.readlines()

    # Last commented line is header
    header = [line for line in lines if line.startswith('#')][-1]

    # Strip line and remove '#' 
    header = header[1:].strip().split()
    header = ['freq' if ee == 'Wave/freq' else ee for ee in header]

    df = pd.read_csv(file_path, delimiter="\s+", names=header, comment='#')
    return df


