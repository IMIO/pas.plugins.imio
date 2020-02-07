# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from pas.plugins.imio.browser.view import AddAuthenticUsers
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_INTEGRATION_TESTING  # noqa
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter

import os
import unittest


class MockupUser:
    def __init__(self, provider, user):
        self.provider = provider
        self.provider.name = "authentic"
        self.user = user
        self.user.provider = self.provider
        self.user.data = {}


def mock_get_authentic_users():
    return {
        "results": [
            {
                u"last_name": u"Suttor",
                u"id": 2,
                u"first_name": u"Beno\xeet",
                u"email": u"benoit.suttor@imio.be",
                u"username": u"bsuttor",
                u"password": u"",
                u"ou": u"default",
            }
        ]
    }


class TestView(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.portal.REQUEST
        acl_users = api.portal.get_tool("acl_users")
        self.plugin = acl_users["authentic"]
        os.environ["service_ou"] = "testou"
        os.environ["service_slug"] = "testslug"
        os.environ["authentic_usagers_hostname"] = "usagers.test.be"

    def test_add_authentic_users(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {}
        data["id"] = "imio"
        data["preferred_username"] = "imiousername"
        data["given_name"] = "imio"
        data["family_name"] = "imio"
        data["email"] = "imio@username.be"
        view = AddAuthenticUsers(self.portal, self.portal.REQUEST)
        self.assertEqual(view.next_url, "http://nohost/plone")
        self.portal.REQUEST.form["next_url"] = "https://www.imio.be"
        view = AddAuthenticUsers(self.portal, self.portal.REQUEST)
        self.assertEqual(view.next_url, "https://www.imio.be")
        view.get_authentic_users = mock_get_authentic_users
        self.assertEqual(
            view.get_authentic_users()["results"][0]["username"], u"bsuttor"
        )
        self.assertEqual(self.plugin._useridentities_by_userid.get("bsuttor"), None)
        view()
        new_user = self.plugin._useridentities_by_userid.get("bsuttor")
        self.assertEqual(new_user.userid, "bsuttor")

    def test_authentic_handler(self):
        view = api.content.get_view(
            name="authentic-handler", context=self.portal, request=self.request
        )
        self.assertIn(
            "authentic-agents", [prov["identifier"] for prov in view.providers()]
        )
        self.assertIn(
            "authentic-usagers", [prov["identifier"] for prov in view.providers()]
        )

    def test_add_authentic_users_get_arg(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.request.form["type"] = "usagers"
        view = getMultiAdapter((self.portal, self.request), name="add-authentic-users")
        self.assertEqual(
            view.authentic_api_url,
            "https://usagers.test.be/api/users/?service-ou=testou&service-slug=testslug",
        )

    def test_usergroup_userprefs(self):
        view = api.content.get_view(
            "usergroup-userprefs", context=self.portal, request=self.request
        )
        self.assertEqual(
            view.get_agent_url(), "https://agents.staging.imio.be/manage/users/"
        )
        self.assertEqual(
            view.get_update_url(),
            "http://nohost/plone/add-authentic-users?type=agents&next_url=http://nohost/plone/@@usergroup-userprefs",
        )
        self.assertIn('<button type="button"', view())
