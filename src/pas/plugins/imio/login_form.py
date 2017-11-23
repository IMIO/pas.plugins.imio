from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api

class LoginFormView(BrowserView):

    def __call__(self):
        """"""
        response = self.request.response
        response.redirect('{0}/authomatic-handler/authentic'.format(api.portal.get().absolute_url()))

