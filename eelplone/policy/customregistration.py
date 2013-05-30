from zope.interface import Interface
from zope.component import getUtility, getAdapter
# from zope.schema import getFieldNamesInOrder

# from five.formlib.formbase import PageForm
from zope import schema
from zope.formlib import form
# from zope.app.form.browser import CheckBoxWidget, ASCIIWidget
# from zope.app.form.interfaces import WidgetInputError, InputErrors
from zope.component import getMultiAdapter

from AccessControl import getSecurityManager
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.utils import normalizeString, safe_unicode

from Products.CMFPlone import PloneMessageFactory as _

# from ZODB.POSException import ConflictError

from Products.statusmessages.interfaces import IStatusMessage

# from plone.app.users.userdataschema import IUserDataSchemaProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget

# import logging

# # Define constants from the Join schema that should be added to the
# # vocab of the join fields setting in usergroupssettings controlpanel.
# JOIN_CONST = ['username', 'password', 'email', 'mail_me']


from plone.app.users.browser.register import BaseRegistrationForm, CantSendMailWidget


class AddUserForm(BaseRegistrationForm):

    label = _(u'heading_add_user_form', default=u'Add New User')
    description = u""
    template = ViewPageTemplateFile('templates/newuser_form.pt')

    @property
    def form_fields(self):
        defaultFields = super(AddUserForm, self).form_fields

        # The mail_me field needs special handling depending on the
        # validate_email property and on the correctness of the mail
        # settings.
        portal = getUtility(ISiteRoot)
        ctrlOverview = getMultiAdapter((portal, self.request),
                                       name='overview-controlpanel')
        mail_settings_correct = not ctrlOverview.mailhost_warning()
        if not mail_settings_correct:
            defaultFields['mail_me'].custom_widget = CantSendMailWidget
        else:
            # Make the password fields optional: either specify a
            # password or mail the user (or both).  The validation
            # will check that at least one of the options is chosen.
            defaultFields['password'].field.required = False
            defaultFields['password_ctl'].field.required = False
            if portal.getProperty('validate_email', True):
                defaultFields['mail_me'].field.default = True
            else:
                defaultFields['mail_me'].field.default = False

        ## We remove the groups field for EEL !!!

        # Append the manager-focused fields
        allFields = defaultFields #+ form.Fields(IAddUserSchema)

        #allFields['groups'].custom_widget = MultiCheckBoxVocabularyWidget

        return allFields

    @form.action(_(u'label_register', default=u'Register'),
                 validator='validate_registration', name=u'register')
    def action_join(self, action, data):
        errors = super(AddUserForm, self).handle_join_success(data)
        #portal_groups = getToolByName(self.context, 'portal_groups')

        securityManager = getSecurityManager()
        canManageUsers = securityManager.checkPermission('Manage users',
                                                         self.context)
        user_id = data['username']

        # We do not do this for EEL !!!

        # try:
            # # Add user to the selected group(s)
            # if 'groups' in data.keys() and canManageUsers:
                # for groupname in data['groups']:
                    # group = portal_groups.getGroupById(groupname)
                    # group.addMember(user_id, REQUEST=self.request)
        # except (AttributeError, ValueError), err:
            # IStatusMessage(self.request).addStatusMessage(err, type="error")
            # return

        IStatusMessage(self.request).addStatusMessage(
            _(u"User added."), type='info')
        self.request.response.redirect(
            self.context.absolute_url() +
            '/@@usergroup-userprefs?searchstring=' + user_id)