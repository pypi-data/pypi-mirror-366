"""
@author: Niels
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Union

import websockets.asyncio.client
from websockets.asyncio.client import ClientConnection

_LOGGER = logging.getLogger(__name__)


class IntenoError(Exception):
    """
    A superclass that covers all errors occuring during the
    connection to a Inteno device
    """


class NotSupportedError(ValueError, IntenoError):
    """
    An error to be raised if a specific feature
    is not supported by the specified device
    """


class IntenoConnectionError(ConnectionError, IntenoError):
    """
    An error to be raised if the connection to the inteno device failed
    """


class InvalidAnswerError(ValueError, IntenoError):
    """
    An error to be raised if the host Inteno device could not answer a request
    """


class BadStatusError(IntenoError):
    """A bad status code was returned."""

    def __init__(
        self,
        endpoint: str,
        code: int,
        reason: Union[str, None] = None,
        response: Dict[str, Any] = {},
    ) -> None:
        """Instantiate exception."""
        self.response = response
        message = (
            f"BadStatusError at {endpoint}. Code: {code}Reason: {reason or 'unknown'}."
        )
        super().__init__(message)


@dataclass
class IntenoDevice:
    hostname: str
    ipaddr: str
    macaddr: str
    network: str
    device: str
    dhcp: bool
    connected: bool
    wireless: bool
    # Only present when connected is True
    active_connections: int = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntenoDevice":
        """
        Create an Inteno device object from a dictionary.
        The dictionary should contain the keys as defined in the dataclasses.
        """
        if data["wireless"]:
            return WirelessIntenoDevice(**data)
        else:
            return WiredIntenoDevice(**data)


@dataclass
class WiredIntenoDevice(IntenoDevice):
    ethport: str = None
    linkspeed: str = None


@dataclass
class WirelessIntenoDevice(IntenoDevice):
    wdev: str = None
    frequency: str = None
    rssi: int = None
    snr: int = None
    idle: int = None
    in_network: int = None
    wme: bool = None
    ps: bool = None
    n_cap: bool = None
    vht_cap: bool = None
    tx_bytes: int = None
    rx_bytes: int = None
    tx_rate: int = None
    rx_rate: int = None


@dataclass
class IntenoInfoKeys:
    """
    A dataclass to hold the keys for the Inteno device information.
    """

    auth: str
    wpa: str


@dataclass
class IntenoInfoMemory:
    """
    A dataclass to hold the memory information of the Inteno device.
    """

    buffers: int
    free: int
    shared: int
    total: int
    used: int


@dataclass
class IntenoInfoSpecs:
    """
    A dataclass to hold the specifications of the Inteno device.
    """

    adsl: bool
    dect: bool
    eth_ports: int
    usb: bool
    vdsl: bool
    voice: bool
    voice_ports: int
    wifi: bool


"""
{'keys': {'auth': 'ZNIEP7EF3PCVN0L1', 'wpa': 'LXP3WQFQXDDZ2X'},
 'memoryKB': {'buffers': 0,
              'free': 262576,
              'shared': 340,
              'total': 487988,
              'used': 225412},
 'specs': {'adsl': False,
           'dect': False,
           'eth_ports': 5,
           'usb': True,
           'vdsl': False,
           'voice': True,
           'voice_ports': 6,
           'wifi': True},
 'system': {'basemac': '44:D4:37:68:EC:2E',
            'boardid': 'EG400R0',
            'brcmver': '502030',
            'bspver': '502030',
            'cfever': '1.0.38-161.189-IOP1.5',
            'cpu_per': 4,
            'date': 'Sat Aug  2 14:20:09 2025',
            'filesystem': 'UBIFS',
            'firmware': 'EG400-X-GNX-4.3.6.190-R-240426_1729',
            'hardware': 'EG400',
            'kernel': '4.1.38',
            'localtime': 1754137209,
            'model': 'EG400X',
            'name': 'Inteno',
            'procs': 155,
            'serialno': 'EG4024H211017231',
            'socmod': '63139',
            'socrev': 'b0',
            'uptime': '10d 7h 35m 44s'}}
"""


@dataclass
class IntenoInfoSystem:
    """
    A dataclass to hold the system information of the Inteno device.
    """

    basemac: str
    boardid: str
    brcmver: str
    bspver: str
    cfever: str
    cpu_per: int
    date: str  # Date in format "Sat Aug  2 14:20:09 2025"
    filesystem: str
    firmware: str
    hardware: str
    kernel: str
    localtime: int  # Unix timestamp
    model: str
    name: str
    procs: int
    serialno: str
    socmod: str
    socrev: str
    uptime: str


@dataclass
class IntenoInfo:
    """
    A dataclass to hold the information of the Inteno device.
    It contains keys, memory, specs, and system information.
    """

    keys: IntenoInfoKeys
    memoryKB: IntenoInfoMemory
    specs: IntenoInfoSpecs
    system: IntenoInfoSystem

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntenoInfo":
        """
        Create an IntenoInfo object from a dictionary.
        The dictionary should contain the keys as defined in the dataclasses.
        """
        keys = IntenoInfoKeys(**data["keys"])
        memory = IntenoInfoMemory(**data["memoryKB"])
        specs = IntenoInfoSpecs(**data["specs"])
        system = IntenoInfoSystem(**data["system"])
        return IntenoInfo(keys=keys, memoryKB=memory, specs=specs, system=system)


class Inteno:
    """
    Interface to communicate with the Inteno over Websocket
    Timeouts are to be set in the given AIO session
    Attributes:
        session     The AIO session
        url         The url for reaching of the Inteno device
                    (i.e. http://192.168.0.10:80)
        username    The username for the Inteno device
        password    The password for the Inteno device
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
    ) -> None:
        """
        Constructor
        """
        while url[-1] == "/":
            url = url[:-1]
        self.url = url
        # prepend ws:// if missing, by inteno API this is the only supported protocol
        if not self.url.startswith("ws"):
            self.url = "ws://{}".format(self.url)
        self.username = username
        self.password = password
        self._session_id = 0
        self._connection: Union[ClientConnection, None] = None
        self._session_token: Union[str, None] = None
        self._expires: Union[str, None] = None
        self._timeout: Union[str, None] = None

    async def _send_rpc_with_id(self, method: str, params: List[Any], id: int) -> None:
        msg = {"jsonrpc": "2.0", "id": id, "method": method, "params": params}
        await self.connection.send(json.dumps(msg))

    async def _send_rpc(self, method: str, params: List[Any]) -> None:
        self._session_id += 1
        await self._send_rpc_with_id(method, params, self._session_id)

    async def _rcv_rpc_with_id(self, id: int) -> Dict[str, Any]:
        """
        Receive a JSON-RPC message from the Inteno device
        Skips messages that do not match the given id.
        """
        try:
            while True:
                response = await self.connection.recv()
                data = json.loads(response)
                if data.get("id") != id:
                    continue
                if "error" in data:
                    raise InvalidAnswerError(f"Error in response: {data['error']}")
                if "result" not in data:
                    raise InvalidAnswerError("No result in response")
                if len(data["result"]) < 2:
                    raise InvalidAnswerError("Result does not contain expected data")
                data = data["result"][1]
                return data
        except websockets.ConnectionClosed as e:
            raise IntenoConnectionError("Connection closed while receiving data") from e
        except json.JSONDecodeError as e:
            raise InvalidAnswerError("Received invalid JSON response") from e

    async def _rcv_rpc(self) -> Dict[str, Any]:
        """
        Receive a JSON-RPC message from the Inteno device
        This will wait for a message with the current session id.
        """
        return await self._rcv_rpc_with_id(self._session_id)

    @property
    def connection(self) -> ClientConnection:
        """
        Returns the current websocket connection.
        If no connection exists, it will create a new one.
        """
        if self._connection is None:
            raise IntenoConnectionError(
                "No connection established. Please connect first."
            )
        return self._connection

    async def _connect(self) -> None:
        """
        Initialize a websocket connection to the Inteno device and log in
        """
        # close prior connection if it exists
        if self._connection is not None:
            try:
                await self._connection.close()
            except Exception as e:
                _LOGGER.error("Error closing previous connection: %s", e)
            self._connection = None
        _LOGGER.debug("Connecting to Inteno at %s", self.url)
        connection = websockets.asyncio.client.connect(
            self.url,
            subprotocols=["ubus-json"],
        )
        self._connection = await connection.__aenter__()

    async def _disconnect(self) -> None:
        """
        Close the websocket connection to the Inteno device
        """
        if self._connection is not None:
            try:
                await self._connection.close()
            except Exception as e:
                _LOGGER.error("Error closing connection: %s", e)
            self._connection = None
            self._session_token = None
            self._expires = None
            self._timeout = None

    async def _login(self) -> None:
        _LOGGER.debug("Logging in to Inteno at %s", self.url)
        # connect to the Inteno device
        await self._connect()
        # request a challenge
        _LOGGER.debug("Requesting challenge from Inteno device")
        await self._send_rpc(  # Step 1: Request challenge
            "call",
            params=[
                "00000000000000000000000000000000",
                "session",
                "login",
                {
                    "username": self.username,
                    "password": self.password,
                },
            ],
        )
        data = await self._rcv_rpc()
        self._session_token = data["ubus_rpc_session"]
        self._expires = data["expires"]
        self._timeout = data["timeout"]

    async def _logout(self) -> None:
        """
        Log out from the Inteno device and close the connection
        """
        await self._disconnect()
        self._session_token = None
        self._expires = None
        self._timeout = None
        _LOGGER.debug("Logged out from Inteno device at %s", self.url)

    def logged_in(self) -> bool:
        """
        Check if the Inteno device is logged in.
        Returns True if logged in, False otherwise.
        """
        return (
            self._session_token is not None
            and self._expires is not None
            and self._timeout is not None
        )

    async def ensure_logged_in(self, force_reconnect: bool = False) -> None:
        """
        Ensure that the Inteno device is logged in.
        If not, it will log in.
        """
        if force_reconnect:
            _LOGGER.debug("Forcing re-login to Inteno device")
            await self._logout()
        if not self.logged_in():
            await self._login()
        else:
            _LOGGER.debug(
                "Already logged in with session token: %s", self._session_token
            )

    async def list_devices(self) -> Dict[str, IntenoDevice]:
        """
        List all devices connected to the Inteno device.
        Returns a list of dictionaries containing device information.
        """
        await self.ensure_logged_in()
        _LOGGER.debug("Listing devices connected to Inteno")
        await self._send_rpc(
            "call",
            params=[self._session_token, "router.network", "clients", {}],
        )
        devices: dict[str, dict] = await self._rcv_rpc()
        _LOGGER.debug("Received devices: %s", devices)
        devices_parsed = {
            key: IntenoDevice.from_dict(value) for key, value in devices.items()
        }
        return devices_parsed

    async def hardware_info(self) -> IntenoInfo:
        """
        Get hardware information of the Inteno device.
        Returns a dictionary containing hardware information.
        """
        await self.ensure_logged_in()
        _LOGGER.debug("Getting hardware info from Inteno")
        await self._send_rpc(
            "call",
            params=[self._session_token, "router.system", "info", {}],
        )
        hardware_info: Dict[str, Any] = await self._rcv_rpc()
        _LOGGER.debug("Received hardware info: %s", hardware_info)
        return IntenoInfo.from_dict(hardware_info)
