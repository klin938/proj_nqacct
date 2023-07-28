import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

LOG_FORMATTER = "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d — %(message)s"

# predefined mapping for user - direct manager
PRELOAD_USER_MANAGERS = {'user1':'mng101', 'user2':'mgr220', 'user3':'ceo01'}

# predefined mapping for user - department
PRELOAD_USER_DEPARTMENTS = {'user1':'Adv - Facility', 'klin':'DICE', 'user8':'Team Wolfpack'}
