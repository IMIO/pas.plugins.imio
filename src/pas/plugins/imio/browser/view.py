# -*- coding: utf-8 -*-
from authomatic import Authomatic
from authomatic.core import User
from pas.plugins.imio import _
from pas.plugins.imio.integration import ZopeRequestAdapter
from pas.plugins.imio.utils import authentic_cfg
from pas.plugins.imio.utils import authomatic_settings
from pas.plugins.imio.utils import getAuthenticPlugin
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFDiffTool.utils import safe_utf8
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PluggableAuthService.events import PrincipalCreated
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging
import os
import requests


logger = logging.getLogger(__file__)


class AddAuthenticUsers(BrowserView):
    def __init__(self, context, request, authentic_type="agents"):
        super(AddAuthenticUsers, self).__init__(context, request)
        config = authentic_cfg()
        if "type" in self.request.form.keys():
            self.authentic_type = self.request.form["type"]
        else:
            self.authentic_type = authentic_type
        self.authentic_config = config.get("authentic-{0}".format(self.authentic_type))
        self.consumer_key = os.getenv(
            "consumer_key_{0}".format(self.authentic_type), "my-consumer-key"
        )
        self.consumer_secret = os.getenv(
            "consumer_secret_{0}".format(self.authentic_type), "my-consumer-secret"
        )

    @property
    def authentic_api_url(self):
        authentic_hostname = self.authentic_config["hostname"]
        ou = os.getenv("service_ou", "default")
        service_slug = os.getenv("service_slug", "default")
        api_url = "https://{0}/api/users/?service-ou={1}&service-slug={2}".format(
            authentic_hostname, ou, service_slug
        )
        return api_url

    def get_authentic_users(self):
        req = requests.get(
            self.authentic_api_url, auth=(self.consumer_key, self.consumer_secret)
        )
        if req.status_code == 200:
            return req.json()
        else:
            raise "Not able to connect to Authentic"

    def __call__(self):
        plugin = getAuthenticPlugin()
        if not self.authentic_config:
            return ""

        result = self.get_authentic_users()
        new_users = 0
        for data in result.get("results", []):
            user = User("authentic-{0}".format(self.authentic_type), **data)
            user.id = user.username
            if not user.username:
                user.id = safe_utf8(user.email)
                user.username = safe_utf8(user.email)
            fullname = "{0} {1}".format(
                safe_utf8(user.first_name), safe_utf8(user.last_name)
            )
            if not fullname.strip():
                user.fullname = user.id
            else:
                user.fullname = safe_utf8(fullname)
            if not plugin._useridentities_by_userid.get(user.id, None):
                # save
                class SimpleAuthomaticResult:
                    def __init__(self, provider, authentic_type, user):
                        self.provider = provider
                        self.provider.name = "authentic-{0}".format(authentic_type)
                        self.user = user
                        self.user.provider = self.provider
                        self.user.data = {}

                # provider = Authentic()
                res = SimpleAuthomaticResult(plugin, self.authentic_type, user)
                # plugin.remember_identity(res)
                useridentities = plugin.remember_identity(res)
                aclu = api.portal.get_tool("acl_users")
                ploneuser = aclu._findUser(aclu.plugins, useridentities.userid)
                # accessed, container, name, value = aclu._getObjectContext(
                #     self.request['PUBLISHED'],
                #     self.request
                # )
                # from Products.PluggableAuthService.interfaces.authservice import _noroles
                # user = aclu._authorizeUser(
                #     user,
                #     accessed,
                #     container,
                #     name,
                #     value,
                #     _noroles
                # )
                notify(PrincipalCreated(ploneuser))
                logmsg = "User {0} added".format(user.id)
                logger.info(logmsg)
                new_users += 1
        import transaction

        transaction.commit()
        message = "{0} users added".format(new_users)
        api.portal.show_message(message=message, request=self.request)
        self.request.response.redirect(api.portal.get().absolute_url())


@implementer(IPublishTraverse)
class AuthenticView(BrowserView):

    template = ViewPageTemplateFile("authentic.pt")

    def publishTraverse(self, request, name):
        if name and not hasattr(self, "provider"):
            self.provider = name
        return self

    @property
    def _provider_names(self):
        cfgs = authentic_cfg()
        if not cfgs:
            raise ValueError("Authomatic configuration has errors.")
        return cfgs.keys()

    def providers(self):
        cfgs = authentic_cfg()
        if not cfgs:
            raise ValueError("Authomatic configuration has errors.")
        for identifier, cfg in cfgs.items():
            entry = cfg.get("display", {})
            cssclasses = entry.get("cssclasses", {})
            record = {
                "identifier": identifier,
                "title": entry.get("title", identifier),
                "iconclasses": cssclasses.get("icon", "glypicon glyphicon-log-in"),
                "buttonclasses": cssclasses.get(
                    "button", "plone-btn plone-btn-default"
                ),
                "as_form": entry.get("as_form", False),
            }
            yield record

    def _add_identity(self, result, provider_name):
        # delegate to PAS plugin to add the identity
        alsoProvides(self.request, IDisableCSRFProtection)
        aclu = api.portal.get_tool("acl_users")
        aclu.authentic.remember_identity(result)
        api.portal.show_message(
            _(
                "added_identity",
                default="Added identity provided by ${provider}",
                mapping={"provider": provider_name},
            ),
            self.request,
        )

    def _remember_identity(self, result, provider_name):
        alsoProvides(self.request, IDisableCSRFProtection)
        aclu = api.portal.get_tool("acl_users")

        aclu.authentic.remember(result)
        api.portal.show_message(
            _(
                "logged_in_with",
                "Logged in with ${provider}",
                mapping={"provider": provider_name},
            ),
            self.request,
        )

    def __call__(self):
        cfg = authentic_cfg()
        if cfg is None:
            return "Authomatic is not configured"
        if not (
            ISiteRoot.providedBy(self.context)
            or INavigationRoot.providedBy(self.context)
        ):
            # callback url is expected on either navigationroot or site root
            # so befor going on redirect
            root = api.portal.get_navigation_root(self.context)
            self.request.response.redirect(
                "{0}/authentic-handler/{1}".format(
                    root.absolute_url(), getattr(self, "provider", "")
                )
            )
            return "redirecting"
        if not hasattr(self, "provider"):
            return self.template()
        if self.provider not in cfg:
            return "Provider not supported"
        if not self.is_anon:
            if self.provider in self._provider_names:
                raise ValueError(
                    "Provider {0} is already connected to current "
                    "user.".format(self.provider)
                )
            # todo: some sort of CSRF check might be needed, so that
            #       not an account got connected by CSRF. Research needed.
            pass
        auth = Authomatic(cfg, secret=authomatic_settings().secret.encode("utf8"))
        result = auth.login(ZopeRequestAdapter(self), self.provider)
        if not result:
            logger.info("return from view")
            # let authomatic do its work
            return
        if result.error:
            return result.error.message
        display = cfg[self.provider].get("display", {})
        provider_name = display.get("title", self.provider)

        if not self.is_anon:
            # now we delegate to PAS plugin to add the identity
            self._add_identity(result, provider_name)
            self.request.response.redirect("{0}".format(self.context.absolute_url()))
        else:
            # now we delegate to PAS plugin in order to login
            self._remember_identity(result, provider_name)
            self.request.response.redirect(
                "{0}/login_success".format(self.context.absolute_url())
            )
        return "redirecting"

    @property
    def is_anon(self):
        return api.user.is_anonymous()
