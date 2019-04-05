# -*- coding: utf-8 -*-
from authomatic import Authomatic
from authomatic.core import User
from pas.plugins.authomatic.interfaces import _
from pas.plugins.authomatic.utils import authomatic_cfg
from pas.plugins.authomatic.utils import authomatic_settings
from pas.plugins.imio.integration import ZopeRequestAdapter
from pas.plugins.imio.utils import getAuthenticPlugin
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFDiffTool.utils import safe_utf8
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging
import requests


logger = logging.getLogger(__file__)


class AddAuthenticUsers(BrowserView):

    def __init__(self, context, request):
        super(AddAuthenticUsers, self).__init__(context, request)
        config = authomatic_cfg()
        self.authentic_config = config.get('authentic', None)
        self.consumer_key = self.authentic_config['consumer_key']
        self.consumer_secret = self.authentic_config['consumer_secret']

    @property
    def authentic_api_url(self):
        authentic_hostname = api.portal.get_registry_record(
            'pas.plugins.imio.authentic_hostname')
        ou = "default"
        api_url = 'https://{0}/api/users/?service-ou={1}'.format(
            authentic_hostname,
            ou
        )
        return api_url

    def get_authentic_users(self):
        req = requests.get(
            self.authentic_api_url,
            auth=(self.consumer_key, self.consumer_secret)
        )
        if req.status_code == 200:
            return req.json()
        else:
            raise 'Not able to connect to Authentic'

    def __call__(self):
        logs = []
        plugin = getAuthenticPlugin()
        if not self.authentic_config:
            return ""

        result = self.get_authentic_users()
        for data in result.get('results', []):
            user = User('authentic', **data)
            user.id = user.username
            fullname = '{0} {1}'.format(
                safe_utf8(user.first_name), safe_utf8(user.last_name))
            if not fullname.strip():
                user.fullname = user.id
            else:
                user.fullname = fullname
            if not plugin._useridentities_by_userid.get(user.id, None):
                # save
                class SimpleAuthomaticResult():
                    def __init__(self, provider, user):
                        self.provider = provider
                        self.provider.name = 'authentic'
                        self.user = user
                        self.user.provider = self.provider
                        self.user.data = {}
                # provider = Authentic()
                res = SimpleAuthomaticResult(plugin, user)
                plugin.remember_identity(res)
                # useridentities = plugin.remember_identity(res)
                # aclu = api.portal.get_tool('acl_users')
                # ploneuser = aclu._findUser(aclu.plugins, useridentities.userid)
                # notify(PrincipalCreated(ploneuser))
                # transaction.commit()
                logmsg = "User {0} Added".format(user.id)
                logs.append(logmsg)
                logger.info(logmsg)
        return '\n'.join(logs)


@implementer(IPublishTraverse)
class AuthenticView(BrowserView):

    template = ViewPageTemplateFile('authentic.pt')

    def publishTraverse(self, request, name):
        if name and not hasattr(self, 'provider'):
            self.provider = name
        return self

    @property
    def _provider_names(self):
        cfgs = authomatic_cfg()
        if not cfgs:
            raise ValueError('Authomatic configuration has errors.')
        return cfgs.keys()

    def providers(self):
        cfgs = authomatic_cfg()
        if not cfgs:
            raise ValueError('Authomatic configuration has errors.')
        for identifier, cfg in cfgs.items():
            entry = cfg.get('display', {})
            cssclasses = entry.get('cssclasses', {})
            record = {
                'identifier': identifier,
                'title': entry.get('title', identifier),
                'iconclasses': cssclasses.get(
                    'icon',
                    'glypicon glyphicon-log-in'
                ),
                'buttonclasses': cssclasses.get(
                    'button',
                    'plone-btn plone-btn-default'
                ),
                'as_form': entry.get('as_form', False),
            }
            yield record

    def _add_identity(self, result, provider_name):
        # delegate to PAS plugin to add the identity
        alsoProvides(self.request, IDisableCSRFProtection)
        aclu = api.portal.get_tool('acl_users')
        aclu.authentic.remember_identity(result)
        api.portal.show_message(
            _(
                'added_identity',
                default='Added identity provided by ${provider}',
                mapping={'provider': provider_name}
            ),
            self.request
        )

    def _remember_identity(self, result, provider_name):
        alsoProvides(self.request, IDisableCSRFProtection)
        aclu = api.portal.get_tool('acl_users')

        aclu.authentic.remember(result)
        api.portal.show_message(
            _(
                'logged_in_with',
                'Logged in with ${provider}',
                mapping={'provider': provider_name}
            ),
            self.request
        )

    def __call__(self):
        cfg = authomatic_cfg()
        if cfg is None:
            return 'Authomatic is not configured'
        if not (
            ISiteRoot.providedBy(self.context) or
            INavigationRoot.providedBy(self.context)
        ):
            # callback url is expected on either navigationroot or site root
            # so bevor going on redirect
            root = api.portal.get_navigation_root(self.context)
            self.request.response.redirect(
                '{0}/authentic-handler/{1}'.format(
                    root.absolute_url(),
                    getattr(self, 'provider', '')
                )
            )
            return 'redirecting'
        if not hasattr(self, 'provider'):
            return self.template()
        if self.provider not in cfg:
            return 'Provider not supported'
        if not self.is_anon:
            if self.provider in self._provider_names:
                raise ValueError(
                    'Provider {0} is already connected to current '
                    'user.'.format(self.provider)
                )
            # todo: some sort of CSRF check might be needed, so that
            #       not an account got connected by CSRF. Research needed.
            pass
        auth = Authomatic(
            cfg,
            secret=authomatic_settings().secret.encode('utf8')
        )
        result = auth.login(
            ZopeRequestAdapter(self),
            self.provider
        )
        logger.info('self.provider: {}'.format(self.provider))
        if not result:
            logger.info('return from view')
            # let authomatic do its work
            return
        if result.error:
            return result.error.message
        display = cfg[self.provider].get('display', {})
        provider_name = display.get('title', self.provider)

        if not self.is_anon:
            # now we delegate to PAS plugin to add the identity
            self._add_identity(result, provider_name)
            self.request.response.redirect(
                '{0}'.format(self.context.absolute_url())
            )
        else:
            # now we delegate to PAS plugin in order to login
            self._remember_identity(result, provider_name)
            self.request.response.redirect(
                '{0}/login_success'.format(self.context.absolute_url())
            )
        return 'redirecting'

    @property
    def is_anon(self):
        return api.user.is_anonymous()
