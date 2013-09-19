"""

    Plone views overrides.

    For more information see

    * http://collective-docs.readthedocs.org/en/latest/views/browserviews.html

"""

# Zope imports
from ZODB.POSException import POSKeyError
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

grok.templatedir("templates_sharing")
grok.layer(IThemeSpecific)


from plone.indexer.decorator import indexer

@indexer(Interface)
def localRoles(object, **kw):
     return list(object.get_local_roles())
grok.global_adapter(localRoles, name="localRoles")
# index connected in configure.zcml
# <adapter name="localRoles" factory=".changesharing.localRoles" />     
     
class ChangeSharing(grok.View):
    """
    Temp page for testing the LDAP integration.

    http://localhost:8080/Plone/@@changesharing
    """

    # use grok.context(Interface) to associate view with the site root
    grok.context(ISiteRoot)
    grok.require('cmf.ManagePortal')

    need_oldowners_message = _(u"You have to select one or more from the old users.")
    need_newowner_message = _(u"You have to select a new user.")
    objects_updated_message = _(u"Objects updated")
    shareholders = {}
    
    #def localRoles(self):
    #    return self.get_local_roles()

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def membership(self):
        return getToolByName(self.context, 'portal_membership')

    def dry_run(self):
        """Do we have to do a dry run ? """
        return self.request.form.get('dry_run', True)

    def delete_old_sharing(self):
        """Do we have to delete old users from the sharing list ? """
        return self.request.form.get('delete_old_sharing', False)

    def path_filter(self):
        """Do we have an old path?"""
        return self.request.form.get('path', '')

    def list_old_users(self):
        """Returns a list of members that have been shared objects
        """
        def locations():
            shareholders = {}
            catalog = getToolByName(self.context, 'portal_catalog')
            results = catalog.searchResults()
            #print "catalog of len = ", len(results)
            for brain in results:
                if not brain.__record_schema__.has_key("localRoles"):
                    continue
                rid = brain.getRID()
                data = catalog.getIndexDataForRID(rid)
                localroles = data["localRoles"]
                #cat
                #localroles = brain.__record_schema__["localRoles"]
                url = brain.getPath()
                #print localroles, url
                #if not hasattr(localroles, '__iter__'):
                #    continue
                #import pdb; pdb.set_trace()
                if localroles:
                    shareholders[url]=localroles
            #                 for lr in localroles:
            #                     
            #                     for creator,roles in lr:
            #                         if creator in oldowners:
            #                             selected = 1
            #                         else:
            #                             selected = 0
            #                         if creator not in shareholders.keys():
            #                         
            #                             shareholders[creator]= dict(id=creator, name=creator, 
            #                                                         objectsandroles=[(brain.getPath(),roles)],
            #                                                         selected=selected)
            #                         else:
            #                             shareholders[creator]['selected'] = selected
            #                             shareholders[creator]['objectsandroles'].append((brain.getPath(),roles))
            return shareholders
        authors = []
        
        oldowners = self.request.form.get('oldusers', [])
        #catalog = getToolByName(self.context, 'portal_catalog')
        #cat = self.catalog()
        for l,sh in locations().iteritems():
            for people,droits in sh:
                if people in self.shareholders.keys():
                    self.shareholders[people].append((l,droits))
                else:
                    self.shareholders[people] = [(l,droits)]
        #return self.shareholders            
        for creator, d in self.shareholders.iteritems():
            if creator in oldowners:
                selected = 1
            else:
                selected = 0
            dic = dict(id=creator, name=creator, selected=selected, files=(creator,d))
            authors.append(dic)
        authors.sort(lambda a, b: cmp(str(a['name']).lower(), str(b['name']).lower()))
        return authors

    ##
    def update(self):
        old_owners = self.request.form.get('oldusers', [])
        new_owner = self.request.form.get('newowner', '')
        path = self.request.form.get('path', '')
        dryrun = self.request.form.get('dry_run', '')
        ret = ''
        userRoles = {}
        #import pdb; pdb.set_trace()
        self.status = []
        if 'submit' in self.request.form:
            portal = getToolByName(self, 'portal_url').getPortalObject() 
            if isinstance(old_owners, str):
                old_owners = [eval(old_owners)]
            elif isinstance(old_owners, list):
                old_owners = [eval(x) for x in old_owners]

            if not new_owner:
                self.status.append(self.need_newowner_message)

            if not old_owners:
                self.status.append(self.need_oldowners_message)

            #if self.status:
            #    return self.template()

            #clean up
            count = 0
            badcount = 0
            old_owners = [c for c in old_owners if c != new_owner]
            query = {'Creator': old_owners}
            newpath = ''
            if path:
                newpath = self.context.portal_url.getPortalObject().getId() + path

            if not dryrun:
                for owner in old_owners:
                    olduser, files = owner
                    for file in files:
                        results = []
                        #print file
                        try:
                            results = self.catalog(path={'query': file[0], 'depth': 0})
                            if len(results):
                                obj = results[0].getObject()
                            #obj = portal.restrictedTraverse(file)
                            if newpath in file[0]:
                                self._change_sharing(obj,new_owner, [x for x,y in old_owners])
                            if base_hasattr(obj, 'reindexObject'):
                                obj.reindexObject()
                            count += 1
                        except POSKeyError: 
                            badcount += 1
            else:
                ret += "%s " % old_owners


            self.status.append(self.objects_updated_message + " (%s)" % count)
            if ret:
                self.status.append(ret)
            if badcount:
                self.status.append("No blob file : %s" % badcount)
        else:
            self.shareholders = {}
        #return self.template()
        

    def _change_sharing(self, obj, new_owner, old_owners):
        """Change object ownership
        """
        # get_local_roles() return sequence like ( ("userid1", ("rolename1", "rolename2")), ("userid2", ("rolename1") )
        roles = obj.get_local_roles()
        user2del = []
        is2del = self.delete_old_sharing()
        for user, local_roles in roles:
            if user in old_owners:
                obj.manage_setLocalRoles(new_owner, list(local_roles))
                if is2del:
                    user2del.append(user)
        if is2del and len(user2del):
            obj.manage_delLocalRoles(user2del)
            #print "manage_delLocalRoles : % s for %s" % (obj.id, user2del)

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
