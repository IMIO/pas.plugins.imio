# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from authomatic.core import User
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class MockupUser():
    def __init__(self, provider, user):
        self.provider = provider
        self.provider.name = 'authentic'
        self.user = user
        self.user.provider = self.provider
        self.user.data = {}


class TestPlugin(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        acl_users = api.portal.get_tool('acl_users')
        self.plugin = acl_users['authentic']

    def test_add_user(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {}
        data['id'] = "imio"
        data['username'] = "imio username"
        authomatic_user = User('authentic', **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        self.assertEqual(
            self.plugin.enumerateUsers(login='')[0]['login'],
            "imio username"
        )
        # aclu = api.portal.get_tool('acl_users')
        # ploneuser = aclu._findUser(aclu.plugins, useridentities.userid)
        # notify(PrincipalCreated(ploneuser))
        # self.plugin.enumerateUsers(login='')

