# -*- coding: utf-8 -*-
from pas.plugins.imio.interfaces import IAuthenticPlugin
from plone import api


def getAuthenticPlugin():
    pas = api.portal.get_tool('acl_users')
    plugin = pas['authentic']
    if IAuthenticPlugin.providedBy(plugin):
        return plugin
    raise KeyError
