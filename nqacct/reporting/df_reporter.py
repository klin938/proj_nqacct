import sys, logging
import pandas as pd

logger = logging.getLogger(__name__)

this = sys.modules[__name__]

this.df = None

def init(data):
    pd.set_option('display.max_rows', None)
    this.df = pd.DataFrame.from_dict(data)

# https://stackoverflow.com/questions/64892690/pandas-set-a-column-as-horizontal-axis
def usage_yearly_group_summary(keystr, datecol, valstr):
    this.df['datecol'] = pd.to_datetime(this.df[datecol], dayfirst=True)
    agg = this.df.groupby(by=[this.df.datecol.dt.year, keystr]).agg({valstr:sum})
    # transform datecol column to be X-axis and use group/owner as index
    pivot_tb = pd.pivot_table(agg, values=valstr, index=[keystr], columns=['datecol'], fill_value=0)
    return pivot_tb
