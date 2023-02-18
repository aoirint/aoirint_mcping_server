from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text


class BedrockPingRecord(BaseModel):
    id: str
    bedrock_server_id: str
    timeout: float
    is_timeout: bool
    version_protocol: int | None
    version_brand: str | None
    version_version: str | None
    latency: float | None
    players_online: int | None
    players_max: int | None
    motd: str | None
    map: str | None
    gamemode: str | None


class BedrockPingRecordApiModel(ABC):
    @abstractmethod
    def get_latest_bedrock_ping_record(
        self, bedrock_server_id: str
    ) -> BedrockPingRecord | None:
        ...

    @abstractmethod
    def create_bedrock_ping_record(
        self,
        bedrock_server_id: str,
        timeout: float,
        is_timeout: bool,
        version_protocol: int | None,
        version_brand: str | None,
        version_version: str | None,
        latency: float | None,
        players_online: int | None,
        players_max: int | None,
        motd: str | None,
        map: str | None,
        gamemode: str | None,
    ) -> BedrockPingRecord:
        ...


class BedrockPingRecordApiModelImpl(BedrockPingRecordApiModel):
    def __init__(self, database_url: str):
        self.engine = create_engine(url=database_url)

    def get_latest_bedrock_ping_record(
        self, bedrock_server_id: str
    ) -> BedrockPingRecord | None:
        with self.engine.connect() as conn:
            row = conn.execute(
                sql_text(
                    """
                        SELECT
                            "id",
                            "bedrock_server_id",
                            "timeout",
                            "is_timeout",
                            "version_protocol",
                            "version_brand",
                            "version_version",
                            "latency",
                            "players_online",
                            "players_max",
                            "motd",
                            "map",
                            "gamemode"
                        FROM "bedrock_ping_records"
                        WHERE
                            "bedrock_server_id" = :bedrock_server_id
                        ORDER BY "created_at" DESC
                        LIMIT 1
                    """,
                ),
                parameters=dict(
                    bedrock_server_id=bedrock_server_id,
                ),
            ).fetchone()

            if row is None:
                return None

            return BedrockPingRecord(
                id=str(row[0]),
                bedrock_server_id=str(row[1]),
                timeout=row[2],
                is_timeout=row[3],
                version_protocol=row[4],
                version_brand=row[5],
                version_version=row[6],
                latency=row[7],
                players_online=row[8],
                players_max=row[9],
                motd=row[10],
                map=row[11],
                gamemode=row[12],
            )

    def create_bedrock_ping_record(
        self,
        bedrock_server_id: str,
        timeout: float,
        is_timeout: bool,
        version_protocol: int | None,
        version_brand: str | None,
        version_version: str | None,
        latency: float | None,
        players_online: int | None,
        players_max: int | None,
        motd: str | None,
        map: str | None,
        gamemode: str | None,
    ):
        with self.engine.connect() as conn:
            with conn.begin():
                row = conn.execute(
                    sql_text(
                        """
                            INSERT INTO "bedrock_ping_records"(
                                "bedrock_server_id",
                                "timeout",
                                "is_timeout",
                                "version_protocol",
                                "version_brand",
                                "version_version",
                                "latency",
                                "players_online",
                                "players_max",
                                "motd",
                                "map",
                                "gamemode"
                            ) VALUES(
                                :bedrock_server_id,
                                :timeout,
                                :is_timeout,
                                :version_protocol,
                                :version_brand,
                                :version_version,
                                :latency,
                                :players_online,
                                :players_max,
                                :motd,
                                :map,
                                :gamemode
                            ) RETURNING id
                        """,
                    ),
                    parameters=dict(
                        bedrock_server_id=bedrock_server_id,
                        timeout=timeout,
                        is_timeout=is_timeout,
                        version_protocol=version_protocol,
                        version_brand=version_brand,
                        version_version=version_version,
                        latency=latency,
                        players_online=players_online,
                        players_max=players_max,
                        motd=motd,
                        map=map,
                        gamemode=gamemode,
                    ),
                ).fetchone()

                return BedrockPingRecord(
                    id=str(row[0]),
                    bedrock_server_id=bedrock_server_id,
                    timeout=timeout,
                    is_timeout=is_timeout,
                    version_protocol=version_protocol,
                    version_brand=version_brand,
                    version_version=version_version,
                    latency=latency,
                    players_online=players_online,
                    players_max=players_max,
                    motd=motd,
                    map=map,
                    gamemode=gamemode,
                )
