import sys, logging, ldap, ldap.filter

logger = logging.getLogger(__name__)

this = sys.modules[__name__]
this.conn = None
this.host = None
this.port = None
this.binddn = None
this.pw = None
this.basedn = None

def init(host, port, binddn, pw, basedn):
    this.host = host
    this.port = port
    this.binddn = binddn
    this.pw = pw
    this.basedn = basedn
    this.url = 'ldap://' + this.host + ':' + this.port

    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    try:
        this.conn = ldap.initialize(this.url)
        this.conn.simple_bind_s(this.binddn, this.pw)
    except ldap.LDAPError:
        raise ldap.LDAPError('URL: {} | BINDDN: {}'.format(this.url, this.binddn))

def close():
    this.conn.unbind()

# https://stackoverflow.com/questions/1835756/using-try-vs-if-in-python
# search_s returns the following when:
# User not exist
# []
# User's attribute not found
# [('CN=user01 user01,OU=Users,OU=CHANGEME CROP,DC=ad,DC=changeme,DC=edu,DC=au', {})]
# User's attribute found
# [('CN=klin,OU=Users,OU=CHANGEME CROP,DC=ad,DC=changeme,DC=edu,DC=au', {'department': [b'Data Intensive Compute Engineering']})]
# [('CN=klin,OU=Users,OU=CHANGEME CROP,DC=ad,DC=changeme,DC=edu,DC=au', {'manager': [b'CN=mgr01,OU=Users,OU=CHANGEME CROP,DC=ad,DC=changeme,DC=edu,DC=au']})]
def get_user_attribute(username, attribute):
    criteria= ldap.filter.filter_format('(&(objectClass=user)(sAMAccountName=%s))', [username])
    attributes = [attribute]
    result = this.conn.search_s(this.basedn, ldap.SCOPE_SUBTREE, criteria, attributes)
    # An empty list or dict is False
    # https://stackoverflow.com/questions/6454894/reference-an-element-in-a-list-of-tuples
    if not result:
        logger.debug('Username {} not found from LDAP {}'.format(username, this.url))
        return False
    elif not result[0][1]:
        logger.debug('Attribute {} not found for username {}'.format(attribute, username))
        return False
    elif not result[0][1][attribute][0]:
        logger.debug('Attribute {} is empty for username {}'.format(attribute, username))
        return False
    else:
        return result[0][1][attribute][0].decode('utf-8')

def get_user_displayname(username):
    name = get_user_attribute(username, 'displayName')
    if name is False:
        return "NO_FOUND"
    else:
        return name

def get_user_manager(username):
    manager = get_user_attribute(username, 'manager')
    if manager is False:
        return 'NOT_FOUND'
    else:
        return manager.split(',')[0].split('=')[1]

# user is the first element in the chain so that we produce a "completed"
# chain, whcih is required in the case that a grouplist manager is also 
# a actual user.
def get_user_management_chain(username):
    chain = [username]
    while not is_ceo(username) and username != 'NOT_FOUND':
        manager = get_user_manager(username)
        chain.append(manager)
        username = manager
    return chain

def is_ceo(username):
    manager = get_user_manager(username)
    if username in ['ceo01', 'boss01'] and username == manager:
        return True
    else:
        return False

def get_user_department(username):
    department = get_user_attribute(username, 'department')
    if department is False:
        return 'NOT_FOUND'
    else:
        return department

