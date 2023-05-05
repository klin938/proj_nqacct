from nqacct.common.utils import epoch2date
import nqacct.common.ldap_helper as ldap_helper
import config.garvan as g

import os, sys, datetime, logging

# Best practice is, in each module, to have a logger defined like this
# root logger "logging" has been configured in the parent (like main)
logger = logging.getLogger(__name__)

data = dict({'group': [], 'owner': [], 'jobnumber': [], 'submission_time': [],
                'start_time': [], 'end_time': [], 'failed': [], 'exit_status': [],
                'ru_wallclock': [], 'ru_utime': [],'ru_stime': [],'slots': [],
                'cpu': [], 'cpuhours': []})
# https://stackoverflow.com/questions/1977362/how-to-create-module-wide-variables-in-python
# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

this.input = None
this.groupby = None
this.grouplist = None
this.period = None
this.years = None

this.checked_groups = {}
this.total_files = 0
this.total_processed = 0
this.total_ingested = 0
this.total_dropped = 0

def init(input, groupby, grouplist, period, years, checked_groups):
     this.input = input
     this.groupby = groupby
     this.period = period

     if grouplist is not None:
         this.grouplist = grouplist.split(',')
     
     if years is not None:
         this.years = years.split(',')
     this.checked_groups = checked_groups

def build():
    
     ldap_helper.init(g.LDAP_HOST, g.LDAP_PORT, g.LDAP_BINDDN, g.LDAP_PW, g.LDAP_BASEDN)
    
     if os.path.isfile(input):
          print('FILE:', input)
          build_dict_from_file(input)
     elif os.path.isdir(input):
          print('DIR:', input)
          for filename in os.listdir(input):
               fp = os.path.join(input, filename)
               build_dict_from_file(fp)
     logger.info("TOTAL - Files: {} | Processed: {} | Ingested: {} | Dropped: {}".format(this.total_files, this.total_processed, this.total_ingested, this.total_dropped))

     ldap_helper.close()
     return data

def build_dict_from_file(file_path):   
     ingested = 0
     dropped = 0
    
     with open (file_path) as fp:
          # start counting index from 1
          for index, line in enumerate(fp, 1):
               acct_rcrd = line.split(':')

               group = acct_rcrd[2].strip()
               username = acct_rcrd[3].strip()
               jobnumber = acct_rcrd[5].strip()
               submission_time = epoch2date(acct_rcrd[8].strip())
               start_time = epoch2date(acct_rcrd[9].strip())
               end_time = epoch2date(acct_rcrd[10].strip())
               failed = acct_rcrd[11].strip()
               exit_status = acct_rcrd[12].strip()
               wallclock = int(acct_rcrd[13].strip())
               utime = float(acct_rcrd[14].strip())
               stime = float(acct_rcrd[15].strip())
               slots = int(acct_rcrd[34].strip())
               cpu = float(acct_rcrd[36].strip())
               cpuhours = round((slots * wallclock) / 3600, 3)

               checked_group = criteria_check(group, username, jobnumber, submission_time)

               if checked_group is not False:
                    group = checked_group
                    add_to_data(group,username,jobnumber,submission_time,
                              start_time,end_time,failed,exit_status,
                              wallclock,utime,stime,slots,cpu,cpuhours)
                    ingested += 1
               else:
                    dropped += 1
          logger.info("FILE: {} | Processed: {} | Ingested: {} | Dropped: {}".format(file_path, index, ingested, dropped))
        
          this.total_processed += index
          this.total_ingested += ingested
          this.total_dropped += dropped
          this.total_files += 1

def criteria_check(group, username, jobnumber, time_stamp):
     
     dt = datetime.datetime.strptime(time_stamp, '%d/%m/%Y')

     if this.years is None or str(dt.year) in this.years:
               pass
     else:
               logger.debug("Dropped ({} {} {} {}): year [{}] not found in {}".format(jobnumber, username, group, dt.year, dt.year, this.years))
               return False
     # we can use match/case here if its 3.10+
     # Here in case of groupby "user", the username will be
     # copyed to the group column and used as the grouping
     # key in the DataFrame.
     if this.groupby == "user":
          grp = username
     elif this.groupby == "group":
          grp = group
     elif this.groupby == "ad_manager":
          pass
          ## TODO
          ## grp = search_ad_mgr(username, grouplist)
     elif this.groupby == "ad_dept":
          if username not in this.checked_groups:
               grp = ldap_helper.get_user_department(username)
               this.checked_groups[username] = grp
               logger.debug("Rectified ({} {} {} {}): AD Department - {}".format(jobnumber, username, group, dt.year, this.checked_groups[username]))
          else:
               grp = this.checked_groups[username]
     else:
          logger.debug("Unsupported groupby type: {}".format(this.groupby))

     if this.grouplist is None or grp in this.grouplist:
          return grp
     else:
          logger.debug("Dropped ({} {} {} {}): {} [{}] not found in {}".format(jobnumber, username, group, dt.year, this.groupby, grp, this.grouplist))
          return False

# This dedicated method allows us to create some "foobar" data easily (if needed)
def add_to_data(group,username,jobnumber,submission_time,
                start_time,end_time,failed,exit_status,
                wallclock,utime,stime,slots,cpu,cpuhours):
     data['group'].append(group)
     data['owner'].append(username)
     data['jobnumber'].append(jobnumber)
     data['submission_time'].append(submission_time)
     data['start_time'].append(start_time)
     data['end_time'].append(end_time)
     data['failed'].append(failed)
     data['exit_status'].append(exit_status)
     data['ru_wallclock'].append(wallclock)
     data['ru_utime'].append(utime)
     data['ru_stime'].append(stime)
     data['slots'].append(slots)
     data['cpu'].append(cpu)
     data['cpuhours'].append(cpuhours)

     logger.debug("Ingested ({} {} {} {}): SLOTS: {} WC: {} CPU: {} CPUHOURS: {}".format(jobnumber, username, group, submission_time, slots, wallclock, cpu, cpuhours))