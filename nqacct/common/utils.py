from config.definitions import ROOT_DIR

import os, datetime

def epoch2date(epochstr, fmt="%d/%m/%Y"):
    dt = datetime.datetime.fromtimestamp(int(epochstr))
    return dt.strftime(fmt)

def valid_path(string):
    if os.path.isabs(string):
        file_path = string
    else:
        file_path = os.path.join(ROOT_DIR, '', string)
        
    if os.path.exists(file_path):
        return file_path
    else:
        raise FileNotFoundError(file_path)