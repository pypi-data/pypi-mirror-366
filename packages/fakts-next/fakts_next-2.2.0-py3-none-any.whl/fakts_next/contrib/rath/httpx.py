from fakts_next.fakts import Fakts
from rath.links.httpx import HttpxLink
from rath.operation import Operation
from pydantic import BaseModel


class FaltsHttpXConfig(BaseModel):
    """FaltsHttpXConfig"""

    endpoint_url: str


class FaktsHttpXLink(HttpxLink):
    """FaktsHttpXLink


    A FaktsHttpXLink is a HttpxLink that retrieves the configuration
    from a passed fakts context.

    """

    fakts_group: str
    """The fakts group within the fakts context to use for configuration"""
    fakts: Fakts
    """ The fakts context to use for configuration"""

    def configure(self, fakt: FaltsHttpXConfig) -> None:
        """Configure the link with the given fakt"""
        self.endpoint_url = fakt.endpoint_url

    async def aconnect(self, operation: Operation) -> None:
        """Connects the link to the server

        This method will retrieve the configuration from the fakts context,
        and configure the link with it. Before connecting, it will check if the
        configuration has changed, and if so, it will reconfigure the link.
        """
        fakt = await self.fakts.aget(self.fakts_group)
        assert isinstance(fakt, dict), "FaktsAIOHttpLink: fakts group is not a dict"
        self.configure(FaltsHttpXConfig(**fakt))  # type: ignore

        return await super().aconnect(operation)
