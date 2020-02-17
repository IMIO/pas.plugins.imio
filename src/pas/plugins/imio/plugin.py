# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from operator import itemgetter
from pas.plugins.authomatic.plugin import AuthomaticPlugin
from pas.plugins.imio.interfaces import IAuthenticPlugin
from plone import api
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces import plugins as pas_interfaces
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.interface import implementer

import logging
import os
import six


logger = logging.getLogger(__name__)
tpl_dir = os.path.join(os.path.dirname(__file__), "browser")

_marker = {}


def manage_addAuthenticPlugin(context, id="authentic", title="", RESPONSE=None, **kw):
    """Create an instance of a Authentic Plugin.
    """
    plugin = AuthenticPlugin(id, title, **kw)
    context._setObject(plugin.getId(), plugin)
    if RESPONSE is not None:
        RESPONSE.redirect("manage_workspace")


manage_addAuthenticPluginForm = PageTemplateFile("www/AuthenticPluginForm", globals())


@implementer(
    IAuthenticPlugin,
    pas_interfaces.IAuthenticationPlugin,
    pas_interfaces.IPropertiesPlugin,
    pas_interfaces.IUserEnumerationPlugin,
    pas_interfaces.IRolesPlugin,
)
class AuthenticPlugin(AuthomaticPlugin):
    """Authentic PAS Plugin
    """

    security = ClassSecurityInfo()
    meta_type = "Authentic Plugin"
    BasePlugin.manage_options

    # Tell PAS not to swallow our exceptions
    _dont_swallow_my_exceptions = True

    # ##
    # pas_interfaces.plugins.IUserEnumaration

    @security.private
    def remember_identity(self, result, userid=None):
        useridentities = super(AuthenticPlugin, self).remember_identity(result, userid)
        if userid is None:
            # remove old plone userid from source_users
            userid = result.user.username
            acl_users = api.portal.get_tool("acl_users")
            source_users = acl_users.source_users
            if self._useridentities_by_userid.get(userid, None) and userid in [
                us.get("id") for us in source_users.enumerateUsers()
            ]:
                try:
                    source_users.doDeleteUser(userid)
                except KeyError:
                    logger.error(
                        "Not able to delete {0} from source_users".format(userid)
                    )
        return useridentities

    @security.private
    def enumerateUsers(
        self,
        id=None,
        login=None,
        exact_match=False,
        sort_by=None,
        max_results=None,
        **kw
    ):
        """-> ( user_info_1, ... user_info_N )
        OVERRIDE OF PARENT because empty search should get all user and not any.

        o Return mappings for users matching the given criteria.

        o 'id' or 'login', in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).

        o If 'exact_match' is False, then 'id' and / or login may be
          treated by the plugin as "contains" searches (more complicated
          searches may be supported by some plugins using other keyword
          arguments).

        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' and 'login' (some plugins may support
          others).

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all users satisfying the criteria.

        o Minimal keys in the returned mappings:

          'id' -- (required) the user ID, which may be different than
                  the login name

          'login' -- (required) the login name

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'editurl' -- (optional) the URL to a page for updating the
                       mapping's user

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid criteria.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """
        if id and login and id != login:
            raise ValueError("plugin does not support id different from login")
        search_id = id or login
        if search_id:
            if not isinstance(search_id, six.string_types):
                raise NotImplementedError("sequence is not supported.")
        else:
            if search_id != "":
                return ()

        pluginid = self.getId()
        ret = list()
        # shortcut for exact match of login/id
        identity = None
        if exact_match and search_id and search_id in self._useridentities_by_userid:
            identity = self._useridentities_by_userid[search_id]
        if identity is not None:
            identity_userid = identity.userid
            if six.PY2 and isinstance(identity_userid, six.text_type):
                identity_userid = identity_userid.encode("utf8")

            ret.append(
                {"id": identity_userid, "login": identity_userid, "pluginid": pluginid}
            )
            return ret

        # non exact expensive search
        for userid in self._useridentities_by_userid:
            user = self._useridentities_by_userid.get(userid, None)
            email = user.propertysheet.getProperty("email", "")
            if not userid and not email:
                logger.warn("None userid found. This should not happen!")
                continue
            if not userid.startswith(search_id) and not email.startswith(search_id):
                logger.debug("not searchable: {0} for {1}".format(search_id, userid))
                continue
            identity = self._useridentities_by_userid[userid]
            identity_userid = identity.userid
            if six.PY2 and isinstance(identity_userid, six.text_type):
                identity_userid = identity_userid.encode("utf8")
            ret.append(
                {"id": identity_userid, "login": identity_userid, "pluginid": pluginid}
            )
            if max_results and len(ret) >= max_results:
                break
        if sort_by in ["id", "login"]:
            return sorted(ret, key=itemgetter(sort_by))
        return ret

    @security.private
    def getRolesForPrincipal(self, user, request=None):
        """ Fullfill RolesPlugin requirements """
        identity = self._useridentities_by_userid.get(user.getId(), None)
        if not identity:
            return ()
        if not identity._identities:
            return ()
        keys = [key for key in identity._identities.keys()]
        provider_id = keys[0]
        if "roles" in identity._identities[provider_id].keys():
            roles = identity._identities[provider_id]["roles"]
            if isinstance(roles, list):
                return tuple(roles)
            else:
                return ()
        else:
            return ()


InitializeClass(AuthenticPlugin)
