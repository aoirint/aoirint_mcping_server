from abc import ABC, abstractmethod

from mcstatus import BedrockServer
from pydantic import BaseModel


class BedrockPingTimeoutError(Exception):
    pass


class BedrockPingRefusedError(Exception):
    pass


class BedrockPingResult(BaseModel):
    version_protocol: int
    version_brand: str
    version_version: str
    latency: float
    players_online: int
    players_max: int
    motd: str
    map: str
    gamemode: str


class BedrockPingRepository(ABC):
    @abstractmethod
    def ping(self, host: str, port: int, timeout: float) -> BedrockPingResult | None:
        ...


class BedrockPingRepositoryImpl(BedrockPingRepository):
    def ping(self, host: str, port: int, timeout: float) -> BedrockPingResult | None:
        try:
            server = BedrockServer.lookup(address=f"{host}:{port}", timeout=timeout)
            response = server.status()

            return BedrockPingResult(
                version_protocol=response.version.protocol,
                version_brand=response.version.brand,
                version_version=response.version.version,
                latency=response.latency,
                players_online=response.players_online,
                players_max=response.players_max,
                motd=response.motd,
                map=response.map,
                gamemode=response.gamemode,
            )
        except TimeoutError:
            raise BedrockPingTimeoutError
        except ConnectionRefusedError:
            raise BedrockPingRefusedError
