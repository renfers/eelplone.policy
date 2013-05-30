# -*- coding:utf-8 -*-

from five import grok
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable

import logging


# Neest TODOs : Implement import_various for additional stuff we need to import... 
#                + complete the unsinstall profile to unimport settings...


class HiddenProfiles(grok.GlobalUtility):

    grok.implements(INonInstallable)
    grok.provides(INonInstallable)
    grok.name('eelplone.policy')

    def getNonInstallableProfiles(self):
        # To avoid these profiles to show up when adding a fresh Plone site...
        # See https://github.com/plone/Products.CMFPlone/blob/master/Products/CMFPlone/interfaces/installable.py
        profiles = [ 
                    'eelplone.policy:uninstall', 
                    'plone.app.ldap:ldap',
                    'Products.LDAPUserFolder:cmfldap',
                   ]
        return profiles



# def import_various(context):
    # """ Import step for configuration that is not handled in XML files.
    # """
    # # Only run step if a flag file is present
    # if context.readDataFile('eelplone.policy.txt') is None:
        # return

    # logger = context.getLogger("eelplone.policy")
    # site = context.getSite()
    # #Now, do something for the site...
    # print "doing nothing for now..."



