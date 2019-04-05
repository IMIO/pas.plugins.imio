# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from pas.plugins.imio.browser.view import AddAuthenticUsers
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


def mock_get_authentic_users():
    return {
        "results": [
            {
                u'last_name': u'Suttor',
                u'id': 2, u'first_name': u'Beno\xeet',
                u'email': u'benoit.suttor@imio.be',
                u'username': u'bsuttor',
                u'password': u'',
                u'ou': u'default'
            }
        ]
    }


class TestView(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        acl_users = api.portal.get_tool('acl_users')
        self.plugin = acl_users['authentic']

    def test_add_authentic_users(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {}
        data['id'] = "imio"
        data['preferred_username'] = "imiousername"
        data['given_name'] = "imio"
        data['family_name'] = "imio"
        data['email'] = "imio@username.be"
        view = AddAuthenticUsers(self.portal, self.portal.REQUEST)
        view.get_authentic_users = mock_get_authentic_users
        self.assertEqual(self.plugin._useridentities_by_userid.get("bsuttor"), None)
        view()
        new_user = self.plugin._useridentities_by_userid.get('bsuttor')
        self.assertEqual(new_user.userid, "bsuttor")
