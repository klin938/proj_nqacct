import nqacct.common.ldap_helper as ldap_helper
import config.garvan as g

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
    # https://stackoverflow.com/questions/53011418/first-column-in-dataframe-lost-after-grouping
    # this align all desired index keys back in the same top row
    agg = agg.reset_index()
    agg = add_displayname_col(keystr, 'Display Name', agg)
    # transform datecol column to be X-axis and use group/owner as index
    pivot_tb = pd.pivot_table(agg, values=valstr, index=[keystr,'Display Name'], columns=['datecol'], fill_value=0)
    return pivot_tb

def add_displayname_col(keystr, newcol_key, df):
    ldap_helper.init(g.LDAP_HOST, g.LDAP_PORT, g.LDAP_BINDDN, g.LDAP_PW, g.LDAP_BASEDN)
    df[newcol_key] = df[keystr].apply(ldap_helper.get_user_displayname)
    ldap_helper.close()
    return df