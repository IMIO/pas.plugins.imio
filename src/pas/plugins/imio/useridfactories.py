# -*- coding: utf-8 -*-
from pas.plugins.authomatic.useridfactories import BaseUserIDFactory
from pas.plugins.imio import _


class ProviderIDEmailFactory(BaseUserIDFactory):

    title = _(u'Provider User Email')

    def __call__(self, plugin, result):
        if getattr(result, 'user', None):
            return self.normalize(plugin, result, result.user.email)
        else:
            return self.normalize(plugin, result, result.get('email'))
