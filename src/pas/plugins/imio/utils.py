# -*- coding: utf-8 -*-
from pas.plugins.authomatic.interfaces import IPasPluginsAuthomaticLayer
from pas.plugins.authomatic.plugin import AuthomaticPlugin
from plone import api


def getAuthenticPlugin():
    pas = api.portal.get_tool('acl_users')
    plugin = pas.objectValues['authentic']
    if IPasPluginsAuthomaticLayer.providedBy(plugin):
        return plugin
    raise KeyError
