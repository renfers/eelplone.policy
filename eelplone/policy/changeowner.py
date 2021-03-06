"""

    Plone views overrides.

    For more information see

    * http://collective-docs.readthedocs.org/en/latest/views/browserviews.html

"""

# Zope imports
from zope.interface import Interface
from five import grok
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr

from zope.component import getMultiAdapter
from plone.memoize.view import memoize

# Local imports
from eelplone.policy.interfaces import IThemeSpecific
from eelplone.policy import messageFactory as _

grok.templatedir("templates")
grok.layer(IThemeSpecific)



class ChangeOwner(grok.View):
    """
    Temp page for testing the LDAP integration.

    http://localhost:8080/Plone/@@changeowner
    """

    # use grok.context(Interface) to associate view with the site root
    grok.context(ISiteRoot)
    grok.require('cmf.ManagePortal')

    need_oldowners_message = _(u"You have to select one or more from the old owners.")
    need_newowner_message = _(u"You have to select a new owner.")
    objects_updated_message = _(u"Objects updated")


    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def membership(self):
        return getToolByName(self.context, 'portal_membership')

    def exclude_members_folder(self):
        """Do we have to exclude the members folder ? """
        return self.request.form.get('exclude_members_folder', True)

    def dry_run(self):
        """Do we have to do a dry run ? """
        return self.request.form.get('dry_run', True)

    def delete_old_creators(self):
        """Do we have to delete old owners from the creators list ? """
        return self.request.form.get('delete_old_creators', False)

    def delete_old_owners(self):
        """Do we have to delete old owners from the owners role list ? """
        return self.request.form.get('delete_old_owners', False)

    def path_filter(self):
        """Do we have an old path?"""
        return self.request.form.get('path', '')

    def list_authors(self):
        """Returns a list of members that have created objects
        """
        authors = []
        oldowners = self.request.form.get('oldowners', [])

        for creator in self.catalog.uniqueValuesFor('Creator'):
            if not creator:
                continue

            info = self.membership.getMemberInfo(creator)
            if info and info['fullname']:
                d = dict(id=creator, name="%s (%s)" % (info['fullname'], creator))
            else:
                d = dict(id=creator, name=creator)

            if creator in oldowners:
                d['selected'] = 1
            else:
                d['selected'] = 0
            authors.append(d)

        authors.sort(lambda a, b: cmp(str(a['name']).lower(), str(b['name']).lower()))
        return authors

    ##
    def update(self):

        old_owners = self.request.form.get('oldowners', [])
        new_owner = self.request.form.get('newowner', '')
        path = self.request.form.get('path', '')
        dryrun = self.request.form.get('dry_run', '')
        ret = ''

        self.status = []
        if 'submit' in self.request.form:

            if isinstance(old_owners, str):
                old_owners = [old_owners]

            if not new_owner:
                self.status.append(self.need_newowner_message)

            if not old_owners:
                self.status.append(self.need_oldowners_message)

            #if self.status:
            #    return self.template()

            #clean up
            old_owners = [c for c in old_owners if c != new_owner]

            members_folder = self.membership.getMembersFolder()
            members_folder_path = None
            if members_folder:
                members_folder_path = '/'.join(self.membership.getMembersFolder().getPhysicalPath())
            query = {'Creator': old_owners}
            if path:
                query['path'] = self.context.portal_url.getPortalObject().getId() + path

            count = 0
            for brain in self.catalog(**query):
                if self.exclude_members_folder() and members_folder_path and \
                   brain.getPath().startswith(members_folder_path):
                    #we dont want to change ownership for the members folder
                    #and its contents
                    continue

                if not dryrun:
                    obj = brain.getObject()
                    self._change_ownership(obj, new_owner, old_owners)
                    self._change_sharing(obj,new_owner, old_owners)
                    if base_hasattr(obj, 'reindexObject'):
                        obj.reindexObject()
                else:
                    ret += "%s " % brain.getPath()

                count += 1

            self.status.append(self.objects_updated_message + " (%s)" % count)
            if ret:
                self.status.append(ret)

        #return self.template()
        

    def _change_sharing(self, obj, new_owner, old_owners):
        """Change object ownership
        """
        # get_local_roles() return sequence like ( ("userid1", ("rolename1", "rolename2")), ("userid2", ("rolename1") )
        roles = obj.get_local_roles()
        for user, local_roles in roles:
            if user in old_owners:
                obj.manage_setLocalRoles(new_owner, list(local_roles))

    def _change_ownership(self, obj, new_owner, old_owners):
        """Change object ownership
        """

        #1. Change object ownership
        # changing the way it retrieve user (member)
        #acl_users = getattr(self.context, 'acl_users')
        #user = acl_users.getUserById(new_owner)
        mt = getToolByName(self.context, 'portal_membership')
        user = mt.getMemberById(new_owner)
        utils = self.context.plone_utils

        if user is None:
            user = self.membership.getMemberById(new_owner)
            if user is None:
                raise KeyError, 'Only retrievable users in this site can be made owners.'
        
        utils.changeOwnership(obj, user)

        #obj.changeOwnership(user)


        #2. Remove old authors if we was asked to and add the new_owner
        #   as primary author
        try:
            creators = list(obj.Creators())
        except:
            print "Not possible to reach Creators on this obj : %s"% obj
            #import pdb; pdb.set_trace()
            creators = list(obj.creators)
        if self.delete_old_creators():
            creators = [c for c in creators if c not in old_owners]

        if new_owner in creators:
        # Don't add same creator twice, but move to front
            del creators[creators.index(new_owner)]

        obj.setCreators([new_owner] + creators)

        #3. Remove the "owner role" from the old owners if we was asked to
        #   and add the new_owner as owner
        if self.delete_old_owners():
            #remove old owners
            owners = [o for o in obj.users_with_local_role('Owner') if o in old_owners]
            for owner in owners:
                roles = list(obj.get_local_roles_for_userid(owner))
                roles.remove('Owner')
                if roles:
                    obj.manage_setLocalRoles(owner, roles)
                else:
                    obj.manage_delLocalRoles([owner])

        roles = list(obj.get_local_roles_for_userid(new_owner))
        if 'Owner' not in roles:
            roles.append('Owner')
            obj.manage_setLocalRoles(new_owner, roles)
