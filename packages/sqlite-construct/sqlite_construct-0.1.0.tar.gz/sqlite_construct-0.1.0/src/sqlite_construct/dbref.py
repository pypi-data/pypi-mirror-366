"""Uniform database reference definition."""

import os

from uritools import urisplit, uricompose


class DB_SCHEME:
    SQLITE3 = "sqlite3"


class DBReferenceError(Exception):
    """Database reference error."""

    pass


class DBReference:
    """A unified interface for storing database resource references."""

    __slots__ = ("scheme", "username", "password", "host", "port", "dbname", "parameters", "uri_parts")

    def __init__(self, reference: str | None = None, **kwargs):
        """Initialize a database reference.

        :param reference:   an RFC 3986 compliant string specifying a database resource reference (URI)
        :param kwargs:      arguments, as expected by uritools.uricompose(). If the 'reference' argument does not define
                            a proper URI, these arguments will be used instead.

        Scheme of a well-formed URI:
            <scheme>://<authority>/<path>?<query>#<fragment>

        where the <authority> further subdivides as follows:
            <user>:<password>@<host>:<port>

        Reference:
        [1] [uritools — URI parsing, classification and composition](https://uritools.readthedocs.io/en/stable/#)
        [2] [RFC 3986: Uniform Resource Identifier (URI): Generic Syntax](https://datatracker.ietf.org/doc/html/rfc3986)
        """
        try:
            if reference is not None:
                self.uri_parts = urisplit(reference.replace(" ", ""))
            else:
                self.uri_parts = urisplit(uricompose(**{k: v.replace(" ", "") for k, v in kwargs.items()}))
        except (TypeError, ValueError) as e:
            source = reference or kwargs
            raise DBReferenceError(f"Create a database reference: {source=}: {e.__class__.__name__}: {e}")

        if scheme := self.uri_parts.getscheme():
            self.scheme = scheme
        else:
            raise DBReferenceError("Create a database reference: Database type (URI scheme) not defined")

        if userinfo := self.uri_parts.getuserinfo():
            userinfo_parts = userinfo.partition(":")
        else:
            userinfo_parts = ("", "", "")

        self.username = userinfo_parts[0] or None
        self.password = userinfo_parts[2] or None

        self.host = str(self.uri_parts.gethost()) if self.uri_parts.gethost() else None
        self.port = str(self.uri_parts.getport()) if self.uri_parts.getport() else None

        if path := self.uri_parts.getpath():
            path = path.removeprefix("/") if path.startswith("//") else path
            self.dbname = os.path.normpath(path)
        else:
            raise DBReferenceError("Create a database reference: Database name (URI path) not defined")

        self.parameters = self.uri_parts.getquerydict()

    @property
    def uri(self):
        """Compose a URI reference string from its individual components."""
        if self.username:
            userinfo = f"{self.username}:{self.password}" if self.password else self.username
        else:
            userinfo = None

        return uricompose(
            scheme=self.scheme,
            userinfo=userinfo,
            host=self.host,
            port=self.port,
            path=self.dbname,
            query=self.parameters,
        )

    def __str__(self):
        """Database reference string representation."""
        return self.uri
