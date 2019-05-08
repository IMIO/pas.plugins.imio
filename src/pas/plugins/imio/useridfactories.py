# -*- coding: utf-8 -*-
from pas.plugins.authomatic.useridfactories import BaseUserIDFactory
from pas.plugins.imio import _


class ProviderIDFactory(BaseUserIDFactory):

    title = _(u"Provider User ID for Authentic")

    def __call__(self, plugin, result):
        if result.provider.name.endswith("agents"):
            return self.normalize(plugin, result, result.user.username)
        else:
            return self.normalize(plugin, result, result.user.email)
