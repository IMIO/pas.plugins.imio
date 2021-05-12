# -*- coding: utf-8 -*-
from plone import api
from plone.app.users.browser.account import AccountPanelForm
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter, UserDataPanel, PersonalPreferencesPanel, \
    UserDataConfiglet
from plone.app.users.userdataschema import checkEmailAddress
from plone.app.users.userdataschema import IUserDataSchema
from plone.app.users.userdataschema import IUserDataSchemaProvider
from Products.CMFPlone import PloneMessageFactory as _
from zope import schema
from zope.browserpage import ViewPageTemplateFile
from zope.interface import implementer


@implementer(IUserDataSchemaProvider)
class UserDataSchemaProvider(object):
    def getSchema(self):
        """
        """
        return IPASUserDataSchema


class IPASUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """

    fullname = schema.TextLine(
        title=_(u"label_full_name", default=u"Full Name"),
        description=_(
            u"help_full_name_creation", default=u"Enter full name, e.g. John Smith."
        ),
        required=False,
        readonly=True,
    )

    email = schema.ASCIILine(
        title=_(u"label_email", default=u"E-mail"),
        description=u"",
        required=True,
        readonly=True,
        constraint=checkEmailAddress,
    )


class PASUserDataPanelAdapter(UserDataPanelAdapter):
    """
    """


class PasUserDataPanel(UserDataPanel):
    """
    """
    def __init__(self, context, request):
        super(PasUserDataPanel, self).__init__(context, request)
        if self.userid:
            pas = api.portal.get_tool("acl_users")
            if self.userid in pas.source_users.listUserIds():
                self.form_fields.get('fullname').field.readonly = False
                self.form_fields.get('email').field.readonly = False


class PasUserDataConfiglet(PasUserDataPanel):
    template = ViewPageTemplateFile(UserDataConfiglet.template.filename)
