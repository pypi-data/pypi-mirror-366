from pydantic import ConfigDict, Field
import ssl
import certifi
import aiohttp
from fakts_next.grants.remote.errors import ClaimError
from fakts_next.grants.remote.models import FaktsEndpoint
from pydantic import BaseModel

from fakts_next.models import ActiveFakts


class ClaimEndpointClaimer(BaseModel):
    """A claimer that claims the configuration from the endpoint

    This claimer is used to claim the configuration from the endpoint.
    This is the default claimer, and it is used by the default
    Remote Grants.


    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    ssl_context: ssl.SSLContext = Field(
        default_factory=lambda: ssl.create_default_context(cafile=certifi.where()),
        exclude=True,
    )
    """ An ssl context to use for the connection to the endpoint"""

    async def aclaim(
        self,
        token: str,
        endpoint: FaktsEndpoint,
    ) -> ActiveFakts:
        """Claims the configuration from the endpoint

        Parameters
        ----------
        token : str
            The token to use to claim the configuration
        endpoint : FaktsEndpoint
            The endpoint to claim the configuration from
        request : FaktsRequest
            The request to use to claim the configuration

        Returns
        -------
        Dict[str, FaktValue]
            The configuration

        Raises
        ------
        ClaimError
            An error occured while claiming the configuration
        """

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_context)) as session:
            async with session.post(
                f"{endpoint.base_url}claim/",
                json={
                    "token": token,
                    "secure": endpoint.base_url.startswith("https"),
                },
            ) as resp:
                data = await resp.json()

                if resp.status == 200:
                    data = await resp.json()
                    if "status" not in data:
                        raise ClaimError("Malformed Answer")

                    status = data["status"]
                    if status == "error":
                        raise ClaimError(data["message"])
                    if status == "granted":
                        return ActiveFakts(**data["config"])
                    if status == "denied":
                        raise ClaimError("Access denied")

                    raise ClaimError(f"Unexpected status: {status}")
                else:
                    raise ClaimError("Error! Coud not claim this app on this endpoint")
