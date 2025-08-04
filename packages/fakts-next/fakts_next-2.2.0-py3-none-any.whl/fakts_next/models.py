from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
import json
from hashlib import sha256


class Alias(BaseModel):
    """An alias is a way of contacting a service instance in Fakts.

    It contains the host, port, ssl flag, path and challenge.
    """

    host: str
    port: Optional[int] = None
    """The port is optional, if not set, the default port for the service will be"""
    ssl: bool = False
    """The ssl flag indicates if the service should be accessed via SSL or not. If set to True, the service will be accessed via HTTPS, otherwise it will be accessed via HTTP."""
    path: Optional[str] = None
    """The path is optional, if not set, the default path for the service will be used."""
    challenge: str = Field(
        default="",
        description="""The challenge is a string that is used to verify the alias. It should be """,
    )

    @property
    def challenge_path(self) -> str:
        """The challenge_path of the alias. Its a reachable http path that can be used to verify if the alias is accessible by the client."""
        return self.to_http_path(self.challenge)

    def to_http_path(self, append: Optional[str] = None) -> str:
        """Convert the alias to a HTTP path

        This method converts the alias to a HTTP path, which can be used to access the service.
        If the port is not set, the default port for the service will be used.
        If the ssl flag is set, the service will be accessed via HTTPS, otherwise it will be accessed via HTTP.

        Args:
            append (Optional[str], optional): An optional string to append to the path. Defaults to None.

        Returns:
            str: The HTTP path for the service
        """
        protocol = "https" if self.ssl else "http"

        url = f"{protocol}://{self.host}"
        if self.port:
            url += f":{self.port}"
        if self.path:
            url += f"/{self.path.lstrip('/')}"
        if append:
            url += f"/{append.lstrip('/')}"

        return url

    def to_ws_path(self, append: Optional[str] = None) -> str:
        """Convert the alias to a WebSocket path

        This method converts the alias to a WebSocket path, which can be used to access the service.
        If the port is not set, the default port for the service will be used.
        If the ssl flag is set, the service will be accessed via wss, otherwise it will be accessed via ws.

        Args:
            append (Optional[str], optional): An optional string to append to the path. Defaults to None.

        Returns:
            str: The WebSocket path for the service
        """
        protocol = "wss" if self.ssl else "ws"

        url = f"{protocol}://{self.host}"
        if self.port:
            url += f":{self.port}"
        if self.path:
            url += f"/{self.path.lstrip('/')}"
        if append:
            url += f"/{append.lstrip('/')}"

        return url


class Instance(BaseModel):
    """Configuration for a service in Fakts."""

    service: str
    identifier: str
    aliases: list[Alias] = []


class AuthFakt(BaseModel):
    """AuthFakt is a special kind of Fakt that is used to authenticate the user with"""

    client_id: str
    client_secret: str
    token_url: str
    scopes: List[str] = Field(default_factory=lambda: ["openid", "profile", "email"])
    """Scopes that this Fakt should request from the user"""


class SelfFakt(BaseModel):
    """SelfFakt is a special kind of Fakt that is used to identify the Fakts server itself"""

    deployment_name: str


class ActiveFakts(BaseModel):
    """The active Fakts are the Fakts that are currently active for this client"""

    self: SelfFakt
    """SelfFakt is a special kind of Fakt that is used to identify the Fakts server itself"""
    auth: AuthFakt
    instances: dict[str, Instance] = {}


class Requirement(BaseModel):
    """A requirement is a way to specify a requirement for a service instance in Fakts."""

    key: str
    service: str
    """ The service is the service that will be used to fill the key, it will be used to find the correct instance. It needs to fullfill
    the reverse domain naming scheme"""
    optional: bool = False
    """ The optional flag indicates if the requirement is optional or not. Users should be able to use the client even if the requirement is not met. """
    description: Optional[str] = None
    """ The description is a human readable description of the requirement. Will be show to the user when asking for the requirement."""


class Manifest(BaseModel):
    """A manifest for an app that can be installed in ArkitektNext

    Manifests are used to describe apps that can be installed in ArkitektNext.
    They provide information about the app, such as the
    its globally unique identifier, the version, the scopes it needs, etc.

    This Manifest is send to the Fakts server on initial app configuration,
    and is used to register the app with the Fakts server, which in turn
    will prompt the user to grant the app access to establish itself as
    an ArkitektNext app (and therefore as an OAuth2 client) (see more in the
    Fakts documentation).

    """

    version: str
    """ The version of the app TODO: Should this be a semver? """
    identifier: str
    """ The globally unique identifier of the app: TODO: Should we check for a reverse domain name? """
    scopes: List[str]
    """ Scopes that this app should request from the user """
    logo: Optional[str] = None
    """ A URL to the logo of the app TODO: We should enforce this to be a http URL as local paths won't work """
    requirements: Optional[List[Requirement]] = Field(default_factory=list)
    """ Requirements that this app has TODO: What are the requirements? """
    model_config = ConfigDict(extra="forbid")

    description: Optional[str] = None
    """ A human readable description of the app """

    def hash(self) -> str:
        """Hash the manifest

        A manifest describes all the  metadata of an app. This method
        hashes the manifest to create a unique hash for the current configuration of the app.
        This hash can be used to check if the app has changed since the last time it was run,
        and can be used to invalidate caches.

        Returns:
            str: The hash of the manifest

        """

        unsorted_dict = self.model_dump()

        # sort the requirements
        unsorted_dict["requirements"] = sorted(unsorted_dict["requirements"], key=lambda x: x["key"])
        # sort the scopes
        unsorted_dict["scopes"] = sorted(unsorted_dict["scopes"])

        # JSON encode the dictionary
        json_dd = json.dumps(unsorted_dict, sort_keys=True)
        # Hash the JSON encoded dictionary
        return sha256(json_dd.encode()).hexdigest()

    @field_validator("identifier", mode="after")
    def check_identifier(cls, v: str) -> str:
        """Check the identifier of the manifest
        This method checks the identifier of the manifest to ensure that it is a valid identifier.
        """
        assert "/" not in v, "The identifier should not contain a /"
        assert len(v) > 0, "The identifier should not be empty"
        assert len(v) < 256, "The identifier should not be longer than 256 characters"
        return v
