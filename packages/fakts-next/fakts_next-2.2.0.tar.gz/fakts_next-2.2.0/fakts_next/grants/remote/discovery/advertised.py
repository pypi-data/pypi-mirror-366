from typing import Dict, AsyncGenerator, List, Tuple, Set
from pydantic import ConfigDict, Field, field_validator
from socket import AF_INET, IPPROTO_UDP
import asyncio
import json
import logging
from pydantic import BaseModel
import ssl
import certifi
from .utils import discover_url
from fakts_next.grants.remote.models import FaktsEndpoint
from fakts_next.grants.remote.errors import DiscoveryError

logger = logging.getLogger(__name__)

DataGram = Tuple[bytes, Tuple[str, int]]


class DiscoveryProtocol(asyncio.DatagramProtocol):
    "The protocol that is used to receive beacons, and put them in a queue"

    def __init__(self, recvq: asyncio.Queue[DataGram]) -> None:
        """Initialize the protocol

        Parameters
        ----------
        recvq : asyncio.Queue
            The queue to put the beacons in
        """
        super().__init__()
        self._recvq = recvq

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Receive a datagram

        This method is called when a datagram is received, and
        puts it in the queue

        Parameters
        ----------
        data : bytes
            The data that was received
        addr : Tuple[str, int]
            The address it was received from
        """
        self._recvq.put_nowait((data, addr))


class ListenBinding(BaseModel):
    """A binding to listen on for beacons"""

    address: str = "0.0.0.0"
    port: int = 45678
    magic_phrase: str = "beacon-fakts_next"

    @field_validator("port")
    def check_port(cls, v: int) -> int:
        if v < 0 or v > 65535:
            raise ValueError(f"Port {v} is not in the valid range")
        return v


class Beacon(BaseModel):
    """A beacon that is received when listening on
    a broadcast port"""

    url: str
    """The url of the endpoint"""


async def alisten(bind: ListenBinding, strict: bool = False) -> AsyncGenerator[Beacon, None]:
    """A generator that listens on a broadcast port for beacons

    This generator listens on a specific binding for beacons.
    It will yield the beacons as it receives.


    Parameters
    ----------
    bind : ListenBinding
        The binding to listen on
    strict : bool, optional
        Should we error on bad Beacons, by default False


    Yields
    ------
    Beacon
        The beacon that was received

    Raises
    ------
    e
        Any exception that is raised by the socket
    """
    transport = None

    try:
        loop = asyncio.get_event_loop()
        read_queue: asyncio.Queue[DataGram] = asyncio.Queue()  # type: ignore
        transport, _ = await loop.create_datagram_endpoint(
            lambda: DiscoveryProtocol(read_queue),
            local_addr=(bind.address, bind.port),  # Change port number here
            family=AF_INET,
            proto=IPPROTO_UDP,
        )

        while True:
            data, _ = await read_queue.get()
            try:
                data = str(data, "utf8")
                if data.startswith(bind.magic_phrase):
                    endpoint = data[len(bind.magic_phrase) :]

                    try:
                        endpoint = json.loads(endpoint)
                        endpoint = Beacon(**endpoint)
                        yield endpoint

                    except json.JSONDecodeError as e:
                        logger.error("Received Request but it was not valid json")
                        if strict:
                            raise e

                else:
                    logger.error(f"Received Non Magic Response {data}. Maybe somebody sends")

            except UnicodeEncodeError as e:
                logger.error("Couldn't decode received message")
                if strict:
                    raise e

    except asyncio.CancelledError as e:
        if transport:
            transport.close()
        logger.info("Stopped checking")
        raise e
    finally:
        if transport:
            transport.close()
        logger.info("Stopped checking")


async def alisten_pure(bind: ListenBinding, strict: bool = False) -> AsyncGenerator[Beacon, None]:
    """A generator that listens on a broadcast port for beacons

    This generator listens on a specific binding for beacons.
    It will yield the beacons as it receives, but will only yield
    each beacon once.


    Parameters
    ----------
    bind : ListenBinding
        The binding to listen on
    strict : bool, optional
        Should we error on bad Beacons, by default False


    Yields
    ------
    Beacon
        The beacon that was received

    Raises
    ------
    e
        Any exception that is raised by the socket
    """

    already_detected: Set[str] = set()

    async for x in alisten(bind, strict):
        if x.url not in already_detected:
            already_detected.add(x.url)
            yield x

    return


class FirstAdvertisedDiscovery(BaseModel):
    """A discovery that will return the first endpoint that is advertised

    This discovery will listen on a broadcast port for beacons.
    It will then try to connect to the endpoint and return it.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    binding: ListenBinding = Field(default_factory=ListenBinding)
    """The address to bind to"""
    strict: bool = False
    """Should we error on bad Beacons"""
    discovered_endpoints: Dict[str, FaktsEndpoint] = Field(default_factory=dict)
    """A cache of discovered endpoints"""
    ssl_context: ssl.SSLContext = Field(
        default_factory=lambda: ssl.create_default_context(cafile=certifi.where()),
        exclude=True,
    )
    """ An ssl context to use for the connection to the endpoint"""
    allow_appending_slash: bool = Field(
        default=True,
        description="If the url does not end with a slash, should we append one? ",
    )
    auto_protocols: List[str] = Field(
        default_factory=lambda: [],
        description="If no protocol is specified, we will try to connect to the following protocols",
    )
    timeout: int = Field(
        default=3,
        description="The timeout for the connection",
    )

    async def adiscover(self) -> FaktsEndpoint:
        """Discover the endpoint

        This method will always return the same endpoint (the one that was
        passed to the constructor)

        Parameters
        ----------
        request : FaktsRequest
            The request to use for the discovery process (is not used)

        Returns
        -------
        FaktsEndpoint
            A valid endpoint
        """

        async for beacon in alisten_pure(self.binding, strict=self.strict):
            try:
                endpoint = await discover_url(beacon.url, self.ssl_context)
                return endpoint
            except Exception as e:
                logger.error(f"Could not connect to beacon {beacon.url}: {e}")
                continue

        raise DiscoveryError("Could not find any endpoint")
