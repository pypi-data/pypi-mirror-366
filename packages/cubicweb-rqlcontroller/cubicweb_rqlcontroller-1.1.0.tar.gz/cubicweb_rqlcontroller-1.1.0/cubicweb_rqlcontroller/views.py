# copyright 2013-2024 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-rqlcontroller views/forms/actions/components for web ui"""

import json
import re

from cubicweb.predicates import (
    ExpectedValuePredicate,
    match_form_params,
    match_http_method,
    anonymous_user,
    authenticated_user,
)
from cubicweb.uilib import exc_message
from cubicweb.utils import json_dumps
from cubicweb_web import RemoteCallFailed, DirectResponse
from cubicweb_web.controller import Controller
from cubicweb_web.views.urlrewrite import rgx_action, SchemaBasedRewriter
from cubicweb import Binary
from cubicweb_rqlcontroller.rql_schema_holder import RqlIOSchemaHolder

from cubicweb_rqlcontroller.predicates import match_all_http_headers, match_basic_auth


ARGRE = re.compile(r"__r(?P<ref>\d+)$")
DATARE = re.compile(r"__f(?P<ref>.+)$")


def rewrite_args(args, output, form):
    for k, v in args.items():
        if not isinstance(v, str):
            continue
        match = ARGRE.match(v)
        if match:
            numref = int(match.group("ref"))
            if 0 <= numref <= len(output):
                rset = output[numref]
                if not rset:
                    raise Exception(f"{v} references empty result set {rset}")
                if len(rset) > 1:
                    raise Exception(f"{v} references multi lines result set {rset}")
                row = rset.rows[0]
                if len(row) > 1:
                    raise Exception(f"{v} references multi column result set {rset}")
                args[k] = row[0]
            continue
        match = DATARE.match(v)
        if match:
            args[k] = Binary(form[v][1].read())


class match_request_content_type(ExpectedValuePredicate):
    """check that the request body has the right content type"""

    def _get_value(self, cls, req, **kwargs):
        header = req.get_header("Content-Type", None)
        if header is not None:
            header = header.split(";", 1)[0].strip()
        return header


class RqlIOSchemaController(Controller):
    __regid__ = "rqlio_schema"
    __select__ = match_http_method("GET", "HEAD")

    def publish(self, rset=None):
        self._cw.set_content_type("application/json")
        self._cw.add_header("Etag", RqlIOSchemaHolder.get_schema_hash(self._cw))
        return json.dumps(RqlIOSchemaHolder.get_schema(self._cw)).encode(
            self._cw.encoding
        )


class BaseRqlIOController(Controller):
    """posted rql queries and arguments use the following pattern:

    [('INSERT CWUser U: U login %(login)s, U upassword %(pw)s',
      {'login': 'babar', 'pw': 'cubicweb rulez & 42'}),
     ('INSERT CWGroup G: G name %(name)s',
      {'name': 'pachyderms'}),
     ('SET U in_group G WHERE G eid %(g)s, U eid %(u)s',
      {'u': '__r0', 'g': '__r1'}),
     ('INSERT File F: F data %(content)s, F data_name %(fname)s',
      {'content': '__f0', 'fname': 'toto.txt'}),
    ]

    The later query is an example of query built to upload binety
    data as a file object. It requires to have a multipart query
    in which there is a part holding a file named '__f0'. See
    cwclientlib for examples of such queries.

    Limitations: back references can only work if one entity has been
    created.

    """

    __abstract__ = True
    __regid__ = "rqlio"
    __select__ = match_http_method("POST") & match_form_params("version")

    def json(self):
        contenttype = self._cw.get_header("Content-Type", raw=False)
        if (contenttype.mediaType, contenttype.mediaSubtype) == (
            "application",
            "json",
        ):  # noqa: E501
            encoding = contenttype.params.get("charset", "utf-8")
            content = self._cw.content
        else:
            # Multipart content is usually built by
            # cubicweb.multipart.parse_form_data() which encodes using
            # "utf-8" by default.
            encoding = "utf-8"
            content = self._cw.form["json"][1]
        try:
            # here we use .read instead of .gevalue because
            # on some circumstances content is an instance of BufferedRandom
            # which has no getvalue method
            args = json.loads(content.read().decode(encoding))
        except ValueError as exc:
            raise RemoteCallFailed(exc_message(exc, self._cw.encoding))
        if not isinstance(args, (list, tuple)):
            args = (args,)
        return args

    def publish(self, rset=None):
        self._cw.ajax_request = True
        self._cw.set_content_type("application/json")

        version = self._cw.form["version"]
        if version not in ("1.0", "2.0"):
            raise RemoteCallFailed("unknown rqlio version %r", version)

        args = self.json()
        try:
            result = self.rqlio(version, *args)
        except (RemoteCallFailed, DirectResponse):
            raise
        except Exception as exc:
            raise RemoteCallFailed(exc_message(exc, self._cw.encoding))
        if result is None:
            return b""
        return json_dumps(result).encode(self._cw.encoding)

    def rqlio(self, version, *rql_args):
        try:
            output = self._rqlio(rql_args)
        except Exception:
            self._cw.cnx.rollback()
            raise
        else:
            self._cw.cnx.commit()
        if version == "2.0":
            return [{"rows": o.rows, "variables": o.variables} for o in output]
        return [o.rows for o in output]

    def _rqlio(self, rql_args):
        output = []
        for rql, args in rql_args:
            if args is None:
                args = {}
            rewrite_args(args, output, self._cw.form)
            output.append(self._cw.execute(rql, args))
            self.log_rql_query(rql, args)
        return output

    def log_rql_query(self, rql: str, args) -> None:
        pass


class JsonRqlIOController(BaseRqlIOController):
    """RqlIOController with csrf desactivated for application/json because
    application/json can't be sent through a form
    """

    __select__ = BaseRqlIOController.__select__ & match_request_content_type(
        "application/json", mode="any"
    )
    require_csrf = False


class MultipartRqlIOController(BaseRqlIOController):
    """RqlIOController with csrf activated for cookie authenticated user
    and multipart/form-data.

    To have csrf deactivated with multipart/form-data, install
    cubicweb-signedrequest and use an authentication method.
    """

    __select__ = (
        BaseRqlIOController.__select__
        & ~match_all_http_headers("Authorization")  # no Authorization == cookie
        & match_request_content_type("multipart/form-data", mode="any")
        & authenticated_user()
    )


class AnonMultipartRqlIOController(BaseRqlIOController):
    """RqlIOController with csrf desactivated for anonymous_user.
    This allows public usage of the route.

    It is expected anonymous user should have only read auhorization.
    """

    __select__ = (
        BaseRqlIOController.__select__
        & ~match_all_http_headers("Authorization")
        & match_request_content_type("multipart/form-data", mode="any")
        & anonymous_user()
    )
    require_csrf = False


class AuthenticatedMultipartRqlIOController(BaseRqlIOController):
    """
    RqlIOController with CSRF check deactivated for a user authenticated by
    Authorization header, for multipart/form-data.

    HTTP Basic Authentication is rejected, as it can be used in an HTML form.
    """

    __select__ = (
        BaseRqlIOController.__select__
        & match_all_http_headers("Authorization")
        & ~match_basic_auth()
        & match_request_content_type("multipart/form-data", mode="any")
        & authenticated_user()
    )
    require_csrf = False


class GetEntitiesRqlIOController(BaseRqlIOController):
    """GetEntitiesRqlIOController allow to get entities attributes
    from a RQL. Only attributes present in the RQL will be sent.
    """

    __regid__ = "rqlio_entities"
    __select__ = match_http_method("POST") & match_request_content_type(
        "application/json", mode="any"
    )
    require_csrf = False

    def publish(self, rset=None):
        self._cw.ajax_request = True
        self._cw.set_content_type("application/json")
        args = self.json()
        rql_args, col = args
        try:
            result = self.get_entities(col, *rql_args)
        except (RemoteCallFailed, DirectResponse):
            raise
        except Exception as exc:
            raise RemoteCallFailed(exc_message(exc, self._cw.encoding))
        if result is None:
            return b""
        return json_dumps(result).encode(self._cw.encoding)

    def get_entities(self, col, *rql_args):
        try:
            return self._get_entities(col, rql_args)
        except Exception:
            self._cw.cnx.rollback()
            raise

    def _get_entities(self, col, rql_args):
        output = []
        for rql, args in rql_args:
            if args is None:
                args = {}
            rewrite_args(args, output, self._cw.form)
            entity_dict_list = []
            for entity in self._cw.execute(rql, args).entities(col=col):
                entity_dict = {"eid": entity.eid}
                for attribute, value in entity.cw_attr_cache.items():
                    if attribute in rql:
                        entity_dict[attribute] = value
                entity_dict_list.append(entity_dict)
            output.append(entity_dict_list)
        return output


class RQLIORewriter(SchemaBasedRewriter):
    rules = [
        (re.compile("/rqlio/schema"), rgx_action(controller="rqlio_schema")),
        (re.compile(r"/rqlio/get_entities"), rgx_action(controller="rqlio_entities")),
        (
            re.compile("/rqlio/(?P<version>.+)$"),
            rgx_action(controller="rqlio", formgroups=("version",)),
        ),
    ]
