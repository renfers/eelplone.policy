"""

    Plone views overrides.

    For more information see

    * http://collective-docs.readthedocs.org/en/latest/views/browserviews.html

"""

import ldap

# Zope imports
from zope.interface import Interface
from five import grok
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName

# Local imports
from interfaces import IThemeSpecific



grok.templatedir("templates")
grok.layer(IThemeSpecific)


BIND_USER = "cn=TCNEELCMSADG,ou=CMS,ou=TCN,dc=EEL"

#BASE_DN = 'ou=ENSEIGNANTS,o=USR,dc=EEL'  # The base DN we use for testing a search.

GROUPS_BASE_DN = 'ou=EEL,o=GRP,dc=EEL'


# LDAP search function that may be reused.
def do_search_groups(ldap_connect_obj, ldap_bind_pass, searchterm):
    #
    results = []

    ldap_connect_obj.simple_bind_s(BIND_USER, ldap_bind_pass)
    filter = '(&(objectClass=ETATGEgroupOfNames)(cn=%s))' % searchterm
    results = ldap_connect_obj.search_s(GROUPS_BASE_DN, 
                                        ldap.SCOPE_SUBTREE, 
                                        filter, 
                                        ['dn', 'member']
                                        )

    return results


##DISABLED - FINALLY DECIDED THAT THIS WOULD NOT BE REQUIRED FOR OUR USE CASES !!!
# class SearchGroups(grok.View):
    # """
    # Temp page for searching groups using LDAPUF API.

    # http://localhost:8080/Plone/@@searchgroups
    # """

    # # use grok.context(Interface) to associate view with the site root
    # grok.context(ISiteRoot)
    # #grok.require('cmf.ManagePortal')

    # groups_number = 0
    # groups = []

    # @property
    # def ldapuf(self):
        # acl_users = getToolByName(self.context, 'acl_users')
        # uf = acl_users['ldap-plugin'].acl_users
        # return uf

    # def update(self):
        # ldapuf = self.ldapuf
        # results = []

        # searchterm = self.request.get('groupname', 'mathematiques')
        # #groups = ldapuf.searchGroups(**{'cn': searchterm})
        # ##groups = ldapuf.getGroups()
        # #self.groups_number = len(groups)
        # #for group in groups:
        # #    print group
        # #    #print dir(group)
        # #    results.append(group)

        # # Initialize LDAP connection
        # ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)

        # ldapuri = "ldaps://ldapedu-rectech1.ceti.etat-ge.ch:636"  # FIXME !!!
        # ldappw = "secret"       # FIXME !!!

        # connection = ldap.initialize(ldapuri)
        # connection.set_option(ldap.OPT_REFERRALS, 0)
        # connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

        # # Do the bind + search
        # groups = do_search_groups(connection, ldappw, searchterm)
        # self.groups = groups
        # self.groups_number = len(groups)

        # for group_dn, group_members in groups:
            # print group_dn
            # print "******"
            # print group_members.get('member', "")

        
        
# class PASSearchGroups(grok.View):
    # """
    # Temp page for searching groups using LDAPUF API.

    # http://localhost:8080/Plone/@@passearchgroups
    # """

    # grok.context(ISiteRoot)
    # grok.require('cmf.ManagePortal')

    # groups = []

    # def update(self):

        # pas = getToolByName(self.context, "acl_users")
        # results = []

        # groupname = self.request.get('groupname', '')
        # if groupname:
            # results = pas.searchGroups(**{'id': groupname})
        # self.groups = [{'group_id':    result['description'], 
                        # 'group_title': result['description'],
                        # 'group_dn':    result['dn'],
                       # } for result in results]
        #print self.groups








