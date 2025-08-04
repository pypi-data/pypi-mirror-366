from typing import Any

from pydantic import BaseModel
from fakts_next.fakts import Fakts
from rath.links.graphql_ws import GraphQLWSLink, Operation


class WebsocketHttpConfig(BaseModel):
    """A WebsocketHttpConfig is a Fakt that can be used to configure the aiohttp client."""

    ws_endpoint_url: str


class FaktsGraphQLWSLink(GraphQLWSLink):
    """FaktsGraphQLWSLink


    A FaktsGraphQLWSLink is a GraphQLWSLink that retrieves the configuration
    from a passed fakts context.

    """

    fakts: Fakts
    """The fakts context to use for configuration"""
    fakts_group: str = "websocket"
    """ The fakts group within the fakts context to use for configuration """

    async def aconfigure(self) -> None:
        """Configure the link with the given fakt"""

        alias = await self.fakts.aget_alias(self.fakts_group)
        self.ws_endpoint_url = alias.to_ws_path("graphql")

    async def aconnect(self, operation: Operation) -> None:
        """Connects the link to the server

        This method will retrieve the configuration from the fakts context,
        and configure the link with it. Before connecting, it will check if the
        configuration has changed, and if so, it will reconfigure the link.
        """

        await self.aconfigure()

        return await super().aconnect(operation)
