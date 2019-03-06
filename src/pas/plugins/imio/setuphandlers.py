# -*- coding: utf-8 -*-
from pkg_resources import parse_version
from plone import api
from plone.api import env
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


HAS_PLONE5 = parse_version(env.plone_version()) >= parse_version('5.0b2')


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'pas.plugins.imio:uninstall',
        ]


def post_install(context):
    """Post install script"""
    if HAS_PLONE5:
        api.portal.set_registry_record(
            'plone.external_login_url',
            u'imio_login'
        )
        api.portal.set_registry_record(
            'plone.external_logout_url',
            u'imio_logout'
        )
    else:
        portal_properties = api.portal.get_tool('portal_properties')
        site_properties = portal_properties.site_properties
        site_properties.external_login_url = u'imio_login'
        site_properties.external_logout_url = u'imio_logout'


def uninstall(context):
    """Uninstall script"""
    if HAS_PLONE5:
        api.portal.set_registry_record(
            'plone.external_login_url',
            u''
        )
        api.portal.set_registry_record(
            'plone.external_logout_url',
            u''
        )
    else:
        portal_properties = api.portal.get_tool('portal_properties')
        site_properties = portal_properties.site_properties
        site_properties.external_login_url = ''
        site_properties.external_logout_url = ''
