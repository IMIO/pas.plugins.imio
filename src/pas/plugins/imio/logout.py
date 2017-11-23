# -*- coding: utf-8 -*-
from plone import api

import requests


def logout_from_authentic(event):
    """
    Logout event handler.

    When user explicitly logs out from the Logout menu, logout from SSO too
    """
    authentic_hostname = api.portal.get_registry_record(
        'pas.plugins.imio.authentic_hostname')
    authentic_logout_url = 'https://{0}/idp/oidc/logout/'.format(
        authentic_hostname
    )
    r = requests.get(authentic_logout_url)  # auth=('user', 'pass'))
    # import pdb; pdb.set_trace()
