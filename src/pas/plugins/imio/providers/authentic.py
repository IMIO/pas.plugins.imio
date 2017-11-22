# -*- coding: utf-8 -*-
"""
|oauth2| Providers
-------------------

Providers which implement the |oauth2|_ protocol.

.. autosummary::

    Authentic
"""

from authomatic.providers.oauth2 import OAuth2
from plone import api
import jwt


__all__ = ['Authentic']


class Authentic(OAuth2):
    """
    """

    @property
    def user_authorization_url(self):
        authentic_hostname = api.portal.get_registry_record(
            'pas.plugins.imio.authentic_hostname')
        return 'https://{0}/idp/oidc/authorize/'.format(authentic_hostname)

    @property
    def access_token_url(self):
        authentic_hostname = api.portal.get_registry_record(
            'pas.plugins.imio.authentic_hostname')
        return 'https://{0}/idp/oidc/token/'.format(authentic_hostname)

    @property
    def user_info_url(self):
        authentic_hostname = api.portal.get_registry_record(
            'pas.plugins.imio.authentic_hostname')
        return 'https://{0}/idp/oidc/user_info/'.format(authentic_hostname)

    @property
    def user_info_scope(self):
        return ['openid', 'email', 'profile']

    @staticmethod
    def _x_user_parser(user, data):
        encoded = data.get('id_token')
        # secret = 'db4d7f78-2996-4ae1-bb4d-02560e74924b'
        if encoded:
            payload_data = jwt.decode(
                encoded,
                algorithms=['RS256'],
                options={'verify_signature': False, 'verify_aud': False}
            )
            if 'sub' in payload_data.keys():
                user.id = user.username = payload_data.get('sub')
        if 'sub' in data.keys():
            # user.id = data.get('sub')
            user.id = data.get('email')
            user.first_name = data.get('given_name')
            user.last_name = data.get('family_name')
            fullname = u'{0} {1}'.format(user.first_name, user.last_name)
            if not fullname.strip():
                user.name = user.id
                user.fullname = user.id
            else:
                user.name = fullname
                user.fullname = fullname
                user.username = fullname
        return user


# The provider type ID is generated from this list's indexes!
# Always append new providers at the end so that ids of existing providers don't change!
PROVIDER_ID_MAP = [Authentic]
