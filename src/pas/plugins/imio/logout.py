# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.utils import transaction_note
from Products.Five import BrowserView


class ImioLogoutFormView(BrowserView):

    def __call__(self):
        """Redirect login to authentic"""

        mt = api.portal.get_tool('portal_membership')
        mt.logoutUser(self.request)
        transaction_note('Logged out')

        authentic_hostname = api.portal.get_registry_record(
            'pas.plugins.imio.authentic_hostname', default=False)
        if not authentic_hostname:
            return
        authentic_logout_url = 'https://{0}/idp/oidc/logout?post_logout_redirect_uri={1}'.format(  # noqa
            authentic_hostname,
            api.portal.get().absolute_url()
        )

        response = self.request.response
        response.redirect(authentic_logout_url)
