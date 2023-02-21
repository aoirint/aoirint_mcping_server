import asyncio
from abc import ABC, abstractmethod

from mcstatus import JavaServer
from pydantic import BaseModel


class JavaPingTimeoutError(Exception):
    pass


class JavaPingRefusedError(Exception):
    pass


class JavaPingResultPlayer(BaseModel):
    id: str
    name: str


class JavaPingResult(BaseModel):
    version_protocol: int
    version_name: str
    latency: float
    players_online: int
    players_max: int
    players_sample: list[JavaPingResultPlayer]
    description: str
    favicon: str | None  # Data URL


class JavaPingRepository(ABC):
    @abstractmethod
    def ping(self, host: str, port: int, timeout: float) -> JavaPingResult | None:
        ...


class JavaPingRepositoryImpl(JavaPingRepository):
    def ping(self, host: str, port: int, timeout: float) -> JavaPingResult | None:
        try:
            server = JavaServer.lookup(address=f"{host}:{port}", timeout=timeout)
            response = server.status()

            # sample is None when no player logged in
            players_sample = (
                response.players.sample if response.players.sample is not None else []
            )

            return JavaPingResult(
                version_protocol=response.version.protocol,
                version_name=response.version.name,
                latency=response.latency,
                players_online=response.players.online,
                players_max=response.players.max,
                players_sample=list(
                    map(
                        lambda player_sample: JavaPingResultPlayer(
                            id=player_sample.id,
                            name=player_sample.name,
                        ),
                        players_sample,
                    )
                ),
                description=response.description,
                favicon=response.favicon,
            )
        except TimeoutError:
            raise JavaPingTimeoutError
        except ConnectionRefusedError:
            raise JavaPingRefusedError
