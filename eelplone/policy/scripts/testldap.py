"""

   Script for testing the LDAP connection.

"""

import sys
import ldap


# TODO : Get the env (rec or prod)... how ? using info in zope.conf ?

REC = {
    'ldapuri': "ldaps://ldapedu-rectech1.ceti.etat-ge.ch:636",
}

PROD = {
    'ldapuri': "ldaps://ldapedu.ge.ch:636",
}

BIND_USER = "cn=TCNEELCMSADG,ou=CMS,ou=TCN,dc=EEL"

BASE_DN = 'ou=ENSEIGNANTS,o=USR,dc=EEL'  # The base DN we use for testing a search.

GROUPS_BASE_DN = 'ou=EEL,o=GRP,dc=EEL'

SSL_CERTIFICATE_PATH = "/etc/ssl/certs/ge-app_CA_self_signed_20080918.pem"

# Function that may be reused.
def do_search(ldap_connect_obj, ldap_bind_pass):
    #
    results = []

    ldap_connect_obj.simple_bind_s(BIND_USER, ldap_bind_pass)
    results = ldap_connect_obj.search_s(BASE_DN, 
                                        ldap.SCOPE_SUBTREE, 
                                        '(objectClass=*)', 
                                        ['cn',]
                                        )

    print "*** LDAP bind and search OK. Search returned %s entries ***" % len(results)


def run():
    # 1) High level script to quickly check things.

    # Usage: ./bin/testldap <bind password> [<env>]
    #        env is optional, defaults to 'rec'.

    args = sys.argv[1:]
    #print args

    # bind password
    ldappw = args[0]

    # server/env data
    env_dict = REC
    if len(args) > 1 and args[1] == 'prod':
        env_dict = PROD

    ldapuri = env_dict['ldapuri']

    # Initialize
    ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)

    l = ldap.initialize(ldapuri)
    l.set_option(ldap.OPT_REFERRALS, 0)
    l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

    #l.set_option(ldap.OPT_DEBUG_LEVEL, 255)

    # Do the bind + search
    do_search(l, ldappw)


def run_require_cert():
    # 2) Low level script to use when we want to check how the bind works regarding the certificate.
    #    Option where we explicitely use the certificate. 

    # Usage: ./bin/testldap_require_cert <bind password> [<env>]
    #        env is optional, defaults to 'rec'.

    args = sys.argv[1:]

    # bind password
    ldappw = args[0]

    # server/env data
    env_dict = REC
    if len(args) > 1 and args[1] == 'prod':
        env_dict = PROD

    ldapuri = env_dict['ldapuri']

    ## Initialize
    ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)

    ldapmodule_trace_level = 1
    ldapmodule_trace_file = sys.stderr
    # Get the cert !!!!!
    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,SSL_CERTIFICATE_PATH)

    l = ldap.initialize(ldapuri,
                        trace_level=ldapmodule_trace_level,
                        trace_file=ldapmodule_trace_file)
    l.set_option(ldap.OPT_REFERRALS, 0)
    l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

    l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
    l.set_option(ldap.OPT_X_TLS_DEMAND, True)

    #l.set_option(ldap.OPT_DEBUG_LEVEL, 255)

    ## Do the bind
    l.bind_s(BIND_USER,ldappw)


def run_ignore_cert():
    # 3) Low level script to use when we want to check how the bind works regarding the certificate.
    #    Option where we ignore the certificate. 

    # Usage: ./bin/testldap_ignore_cert <bind password> [<env>]
    #        env is optional, defaults to 'rec'.

    args = sys.argv[1:]

    # bind password
    ldappw = args[0]

    # server/env data
    env_dict = REC
    if len(args) > 1 and args[1] == 'prod':
        env_dict = PROD

    ldapuri = env_dict['ldapuri']

    ## Initialize
    ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)

    ldapmodule_trace_level = 1
    ldapmodule_trace_file = sys.stderr
    # Ignore the cert !!!!!
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    l = ldap.initialize(ldapuri,
                        trace_level=ldapmodule_trace_level,
                        trace_file=ldapmodule_trace_file)
    l.set_option(ldap.OPT_REFERRALS, 0)
    l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

    l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
    l.set_option(ldap.OPT_X_TLS_DEMAND, True)
    
    #l.set_option(ldap.OPT_DEBUG_LEVEL, 255)

    ## Do the bind
    l.bind_s(BIND_USER,ldappw)


####################################################################################
# Additional testing scripts
####################################################################################

def search_groups():

    # Usage: ./bin/search_groups <bind password> <searchterm> <env>
    #        env is optional, defaults to 'rec'.

    args = sys.argv[1:]
    print args

    # bind password
    ldappw = args[0]

    # search term 
    searchterm = args[1]

    # server/env data
    env_dict = REC
    if len(args) > 1 and args[1] == 'prod':
        env_dict = PROD

    ldapuri = env_dict['ldapuri']

    ## Initialize
    ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)

    #ldapmodule_trace_level = 1
    #ldapmodule_trace_file = sys.stderr
    # Ignore the cert !!!!!
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    l = ldap.initialize(ldapuri,
                        #trace_level=ldapmodule_trace_level,
                        #trace_file=ldapmodule_trace_file
                        )
    l.set_option(ldap.OPT_REFERRALS, 0)
    l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

    l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
    l.set_option(ldap.OPT_X_TLS_DEMAND, True)

    # Do the bind + search
    l.simple_bind_s(BIND_USER, ldappw)
    filter = '(&(objectClass=ETATGEgroupOfNames)(cn=%s))' % searchterm
    results = l.search_s(GROUPS_BASE_DN, 
                         ldap.SCOPE_SUBTREE, 
                         filter, 
                         ['dn',]
                         )
    print "*** LDAP bind and groups search OK. Search returned %s groups ***" % len(results)
    for res in results:
        print res[0]
