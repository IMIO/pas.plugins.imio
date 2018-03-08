# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'pas.plugins.imio:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    site_properties = api.portal.get_tool('portal_properties').site_properties
    site_properties.external_login_url = u'imio_login'
    site_properties.external_logout_url = u'imio_logout'


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
    site_properties = api.portal.get_tool('portal_properties').site_properties
    site_properties.external_login_url = ''
    site_properties.external_logout_url = ''
