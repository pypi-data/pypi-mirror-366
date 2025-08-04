import asyncio
import contextvars
import logging
from typing import Any, Dict, Type
from koil.composition import KoiledModel
from koil.helpers import unkoil
from pydantic import Field
from typing import Optional
from fakts_next.errors import GroupNotFound, NoFaktsFound
from fakts_next.cache.nocache import NoCache
from .protocols import FaktsCache, FaktsGrant
from .models import ActiveFakts, Alias, Manifest
from oauthlib.oauth2.rfc6749.clients.backend_application import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import InvalidClientError
import aiohttp
from oauthlib.common import urldecode
import ssl
import certifi
from ssl import SSLContext


logger = logging.getLogger(__name__)
current_fakts_next: contextvars.ContextVar[Optional["Fakts"]] = contextvars.ContextVar(
    "current_fakts_next", default=None
)


class Fakts(KoiledModel):
    """Fakts is any asynchronous configuration loader.

    Fakts provides a way to concurrently load and access configuration from different
    sources in async and sync environments.

    It is used to load configuration from a grant, and to access it in async
    and sync code.

    A grant constitutes the way to load configuration. It can be a local config file
    (eg. yaml, toml, json), environemnt variables, a remote configuration (eg. from
    a fakts server) a database, or any other source.  It will be loaded either on
    call to `load`,  or on  a call to `get` (if auto_load is set to true).

    Additionaly you can compose grants with the help of meta grants in order to
    load configuration from multiple sources.

    Example:
        ```python
        async with Fakts(grant=YamlGrant("config.yaml")) as fakts:
            config = await fakts.aget("group_name")
        ```

        or

        ```python
        with Fakts(grant=YamlGrant("config.yaml")) as fakts:
            config = await fakts.get("group_name")
        ```

    Fakts should be used as a context manager, and will set the current fakts context
    variable to itself, letting you access the current fakts instance from anywhere in
    your code (async or sync). To understand how the async sync code access work,
    please check out the documentation for koil.


    Example:
        ```python
        async with Fakts(grant=FailsafeGrant(
            grants=[
                EnvGrant(),
                YamlGrant("config.yaml")
            ]
        )) as fakts:
            config = await fakts.get("group_name")
        ```
        In this example fakts will load the configuration from the environment
        variables first, and if that fails, it will load it from the yaml file.


    """

    cache: FaktsCache = Field(default_factory=NoCache, exclude=True)

    """" Requirmements """
    manifest: Manifest

    """"The manifest of the fakts. This is used to describe the fakts and its capabilities."""
    ssl_context: SSLContext = Field(
        default_factory=lambda: ssl.create_default_context(cafile=certifi.where())
    )

    grant: FaktsGrant
    """The grant to load the configuration from"""

    hard_fakts: ActiveFakts | None = Field(default=None, exclude=True)
    """Hard fakts are fakts that are set by the user and cannot be overwritten by grants"""

    loaded_fakts: ActiveFakts | None = Field(default=None, exclude=True)
    """The currently loaded fakts. Please use `get` to access the fakts"""

    alias_map: Dict[str, Alias] = Field(
        default_factory=dict,
        exclude=True,
        description="Map of service names to active aliases",
    )

    loaded_token: Optional[str] = Field(
        default=None, exclude=True, description="The currently loaded token"
    )

    allow_auto_load: bool = Field(
        default=True, description="Should we autoload on get?"
    )
    """Should we autoload the grants on a call to get?"""

    load_on_enter: bool = False
    """Should we load on connect?"""
    delete_on_exit: bool = False
    """Should we delete on connect?"""

    refetch_on_group_not_found: bool = False

    _loaded: bool = False
    _lock: Optional[asyncio.Lock] = None
    _token_lock: Optional[asyncio.Lock] = None
    _alias_lock: Optional[asyncio.Lock] = None

    async def arefresh_token(self, allow_refresh: bool = True) -> str:
        """Refresh the authentication token for a service (async)"""
        """Get Authentikation Token for a service (async)"""
        assert self._lock is not None, (
            "You need to enter the context first before calling this function"
        )
        async with self._lock:
            if not self.loaded_fakts:
                try:
                    await self.aload()
                except Exception as e:
                    logger.error(e, exc_info=True)
                    raise e

        assert self.loaded_fakts, "No fakts loaded yet. Please call load() first."

        scope = " ".join(self.loaded_fakts.auth.scopes)

        auth_client = BackendApplicationClient(
            client_id=self.loaded_fakts.auth.client_id,
            scope=scope,
        )

        token_url = self.loaded_fakts.auth.token_url

        body = auth_client.prepare_request_body(
            client_secret=self.loaded_fakts.auth.client_secret,
            client_id=self.loaded_fakts.auth.client_id,
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }

        data = dict(urldecode(body))

        print("Challening for token with data:", data, token_url)

        # Create an OAuth2 session for the OSF
        async with aiohttp.ClientSession(
            connector=(
                aiohttp.TCPConnector(ssl=self.ssl_context) if self.ssl_context else None
            ),
            headers=headers,
        ) as session:
            async with session.post(
                token_url,
                data=data,
                auth=aiohttp.BasicAuth(
                    self.loaded_fakts.auth.client_id,
                    self.loaded_fakts.auth.client_secret,
                ),
            ) as resp:
                text = await resp.text()

                try:
                    auth_client.parse_request_body_response(text, scope=scope)
                except InvalidClientError as e:
                    logger.error(
                        f"Invalid client error while trying to get token for {self.loaded_fakts.auth.client_id} with response: {text}. We are trying to reload the fakts."
                    )
                    if not allow_refresh:
                        raise e

                    await self.aload(reload=True)
                    return await self.arefresh_token(allow_refresh=False)

                token = auth_client.token
                self.loaded_token = str(token["access_token"])
                return str(token["access_token"])

    async def achallenge_alias(self, alias: Alias) -> bool:
        async with aiohttp.ClientSession(
            connector=(
                aiohttp.TCPConnector(ssl=self.ssl_context) if self.ssl_context else None
            ),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            },
        ) as session:
            async with session.get(
                alias.challenge_path,
            ) as resp:
                # Check status code
                if resp.status != 200:
                    logger.error(
                        f"Failed to challenge alias {alias} with status code {resp.status}"
                    )
                    return False
                else:
                    return True

        return False

    async def aget_token(self) -> str:
        """Refresh the authentication token for a service (async)"""
        """Get Authentikation Token for a service (async)"""
        assert self._token_lock is not None, (
            "You need to enter the context first before calling this function"
        )
        async with self._token_lock:
            if not self.loaded_token:
                try:
                    await self.arefresh_token()
                except Exception as e:
                    logger.error(e, exc_info=True)
                    raise e

        assert self.loaded_token, "No token loaded yet. Please call load() first."
        return self.loaded_token

    async def aload(self, reload: bool = False) -> ActiveFakts:
        """Load the fakts from the grant (async)

        This method will load the fakts from the grant, and set the loaded_fakts
        attribute to the loaded fakts. If the fakts are already loaded, it will
        return the loaded fakts.

        Returns:
            ActiveFakts: The loaded fakts
        """
        if self.cache and not reload:
            cached_fakts = await self.cache.aload()
            if cached_fakts:
                self.loaded_fakts = cached_fakts
                return self.loaded_fakts

        self.loaded_fakts = await self.grant.aload()
        await self.cache.aset(self.loaded_fakts)
        return self.loaded_fakts

    async def arefresh(self):
        """Refresh the fakts (async)

        This method will refresh the fakts by calling the grant's refresh method.
        It will also update the loaded_fakts attribute and cache.
        """
        if not self.loaded_fakts:
            await self.aload(reload=True)
        else:
            self.loaded_fakts = await self.grant.arefresh(self.loaded_fakts)
            await self.cache.aset(self.loaded_fakts)

        return self.loaded_fakts

    async def arefresh_alias(
        self,
        service_name: Optional[str] = None,
        omit_challenge: bool = False,
        cache: bool = True,
        store: bool = True,
    ) -> Alias:
        """Refresh the alias for a service (async)

        This method will refresh the alias for a service, by calling the challenge path
        of the alias. If the challenge fails, it will raise an exception.

        Args:
            service_name (str): The name of the service to refresh the alias for
            cache (bool, optional): Should we cache the alias? Defaults to True.
            store (bool, optional): Should we store the alias in the cache? Defaults to True.

        Returns:
            Alias: The refreshed alias
        """
        assert self._lock is not None, (
            "You need to enter the context first before calling this function"
        )
        async with self._lock:
            if not self.loaded_fakts:
                try:
                    await self.aload()
                except Exception as e:
                    logger.error(e, exc_info=True)
                    raise e

        assert self.loaded_fakts, "No fakts loaded yet. Please call load() first."
        assert service_name in self.loaded_fakts.instances, (
            f"Service {service_name} not found in loaded fakts. Available services: {', '.join(self.loaded_fakts.instances.keys())}"
        )

        service_instance = self.loaded_fakts.instances[service_name]

        for alias in service_instance.aliases:
            if omit_challenge:
                # If we omit the challenge, we just return the alias
                self.alias_map[service_name] = alias
                return alias

            try:
                challenge_ok = await asyncio.wait_for(
                    self.achallenge_alias(alias), timeout=3
                )
                if challenge_ok:
                    self.alias_map[service_name] = alias
                    return alias
            except asyncio.TimeoutError as e:
                logger.error(
                    f"Timeout while challenging alias {alias} for service {service_name}.",
                    exc_info=True,
                )
                continue

        raise GroupNotFound(
            f"Could not find a valid alias for service {service_name}. Available aliases: {', '.join([str(alias.challenge_path) for alias in service_instance.aliases])} all failed to challenge."
        )

    async def aget_alias(
        self,
        fakts_key: Optional[str] = None,
        omit_challenge: bool = False,
        cache: bool = True,
        store: bool = True,
    ) -> Alias:
        """Get Fakt Value (async)

        Gets the currently active configuration for the group_name, by loading it from
        the grant if it is not already loaded.

        Steps:
            1. Acquire lock
            2. If not yet loaded and auto_load is True, load
            4. Return groups fakts

        Args:
            group_name (str): The group name in the fakts
            auto_load (bool, optional): Should we autoload the configuration
                                        if nothing has been set? Defaults to True.
            force_refresh (bool, optional): Should we force a refresh of the grants.
                                            Grants can decide their own refresh logic?
                                            Defaults to False.

        Returns:
            dict: The active fakts
        """
        assert self._alias_lock is not None, (
            "You need to enter the context first before calling this function"
        )
        async with self._alias_lock:
            if fakts_key not in self.alias_map:
                # If we don't have the alias in the map, we need to refresh it
                try:
                    await self.arefresh_alias(fakts_key, omit_challenge=omit_challenge)
                except GroupNotFound as e:
                    logger.error(e, exc_info=True)
                    raise e

        assert fakts_key in self.alias_map, (
            f"Alias for key {fakts_key} not found in alias map. Available aliases: {', '.join(self.alias_map.keys())}"
        )
        return self.alias_map[fakts_key]

    def get_alias(
        self,
        fakts_key: Optional[str] = None,
        cache: bool = True,
        omit_challenge: bool = False,
        store: bool = True,
    ) -> Alias:
        """Get Fakt Value (sync)

        Gets the currently active configuration for the group_name, by loading it from
        the grant if it is not already loaded.

        Steps:
            1. Acquire lock
            2. If not yet loaded and auto_load is True, load
            4. Return groups fakts

        Args:
            group_name (str): The group name in the fakts
            auto_load (bool, optional): Should we autoload the configuration
                                        if nothing has been set? Defaults to True.
            force_refresh (bool, optional): Should we force a refresh of the grants.
                                            Grants can decide their own refresh logic?
                                            Defaults to False.

        Returns:
            dict: The active fakts
        """
        return unkoil(
            self.aget_alias,
            fakts_key,
            cache=cache,
            store=store,
            omit_challenge=omit_challenge,
        )

    def get_token(self) -> str:
        """Get Authentikation Token for a service (sync)

        This method will return the currently loaded token, or refresh it if it is not
        loaded yet. It will raise an exception if the token could not be loaded.

        Returns:
            str: The currently loaded token
        """
        return unkoil(self.aget_token)

    async def __aenter__(self) -> "Fakts":
        """Enter the context manager

        This method will set the current fakts context variable to itself,
        and create locks, to make sure that only one fakt request is
        processed at a time.
        """

        current_fakts_next.set(
            self
        )  # TODO: We should set tokens, but depending on async/sync this is shit
        self._lock = asyncio.Lock()
        self._token_lock = asyncio.Lock()
        self._alias_lock = asyncio.Lock()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        """Exit the context manager and clean up"""
        current_fakts_next.set(
            None
        )  # TODO: And here we should reset, but can't because of koil unsafe thread

    def _repr_html_inline_(self) -> str:
        """(Internal) HTML representation for jupyter"""
        return f"<table><tr><td>grant</td><td>{self.grant.__class__.__name__}</td></tr></table>"


def get_current_fakts_next() -> Fakts:
    """Get the current fakts instance

    This method will return the current fakts instance, or raise an
    exception if no fakts instance is set.

    Returns
    -------
    Fakts
        The current fakts instance
    """
    fakts = current_fakts_next.get()

    if fakts is None:
        raise NoFaktsFound("No fakts instance set in this context")

    return fakts
