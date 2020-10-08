# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from authomatic.core import User
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class MockupUser:
    def __init__(self, provider, user):
        self.provider = provider
        self.provider.name = "authentic-agents"
        self.user = user
        self.user.provider = self.provider
        self.user.data = {}


class TestPlugin(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        acl_users = api.portal.get_tool("acl_users")
        self.plugin = acl_users["authentic"]

    def test_add_user(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {}
        data["id"] = "imio"
        data["username"] = "imiousername"
        data["email"] = "imio@username.be"
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        new_user = self.plugin._useridentities_by_userid.get("imiousername")
        self.assertEqual(new_user.userid, "imiousername")

    def test_enumerate_users(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {"id": "imio", "username": "imio username", "email": "imio@username.be"}
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        self.assertEqual(
            self.plugin.enumerateUsers(login="")[0]["login"], "imio username"
        )
        self.assertEqual(self.plugin.enumerateUsers(login="james"), [])
        data = {"id": "jamesbond", "username": "jamesbond", "email": "james@bond.co.uk"}
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        self.assertEqual(
            self.plugin.enumerateUsers(login="james"),
            [{"login": "jamesbond", "pluginid": "authentic", "id": u"jamesbond"}],
        )

    def test_search_all_users(self):
        count_users = 1
        users = api.user.get_users()
        if "admin" in [user.id for user in users]:
            count_users += 1
        self.assertEqual(len(users), count_users)
        data = {"id": "imio", "username": "imio username", "email": "imio@username.be"}
        authomatic_user = User("authentic", **data)
        mockup_user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(mockup_user)
        users = api.user.get_users()
        count_users += 1
        self.assertEqual(len(users), count_users)
        self.assertIn("imio username", [user.id for user in users])
