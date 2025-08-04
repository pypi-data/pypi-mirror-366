from fakts_next.models import ActiveFakts
from ..errors import GrantError
import logging

from .models import Demander, Discovery, Claimer
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


Token = str
EndpointUrl = str


class RemoteGrantError(GrantError):
    """Base class for all remotegrant errors"""


class RemoteGrant(BaseModel):
    """Abstract base class for remote grants

    A Remote grant is a grant that connects to a fakts_next server,
    and tires to establishes a secure relationship with it.

    This is a highly configurable grant, that can be used to
    dynaimcially *discover* the endpoint, *demand* a token
    to access a token, and then *claim* the configuration
    from the endpoint.

    This grant is highly configurable, and can be used to
    implement any kind of remote grant.

    You can use a specific builder to build a remote grant
    that fits your needs.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    discovery: Discovery
    """The discovery mechanism to use for finding the endpoint"""

    demander: Demander
    """The demander mechanism to use for demanding the token FROM the endpoint"""

    claimer: Claimer
    """The claimer mechanism to use for claiming the token FROM the endpoint"""

    async def aload(self) -> ActiveFakts:
        """Load the configuration

        This function will first discover the endpoint, then demand a token from it,
        and then claim the configuration from it.

        Parameters
        ----------
        request : FaktsRequest
            The request to use for the load

        Returns
        -------
        Dict[str, FaktValue]
            The configuration that was claimed from the endpoint



        """
        try:
            endpoint = await self.discovery.adiscover()
        except Exception as e:
            raise RemoteGrantError(f"Could not discover endpoint: {e}") from e

        token = await self.demander.ademand(endpoint)

        return await self.claimer.aclaim(token, endpoint)
