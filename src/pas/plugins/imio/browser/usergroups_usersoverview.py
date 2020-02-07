# -*- coding: utf-8 -*-
"""
PLONE 5 ONLY
"""
from plone import api
from Products.CMFPlone.controlpanel.browser.usergroups_usersoverview import (
    UsersOverviewControlPanel,
)

import os


class ImioUsersOverviewControlPanel(UsersOverviewControlPanel):
    def get_agent_url(self):
        url = "https://{0}/manage/users/".format(
            os.environ.get("authentic_agents_hostname", "")
        )
        return url

    def get_update_url(self):
        url = "{0}/add-authentic-users?type=agents&next_url={1}".format(
            api.portal.get().absolute_url(),
            "{0}/@@usergroup-userprefs".format(self.context.absolute_url()),
        )
        return url