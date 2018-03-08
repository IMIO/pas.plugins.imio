# -*- coding: utf-8 -*-
from plone import api
from Products.Five import BrowserView


class ImioLoginFormView(BrowserView):

    def __call__(self):
        """Redirect login to authentic"""
        response = self.request.response
        response.redirect('{0}/authomatic-handler/authentic'.format(
            api.portal.get().absolute_url())
        )
