from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text


class CreateJavaPingRecordJavaPingRecordPlayer(BaseModel):
    player_id: str
    name: str


class JavaPingRecordPlayer(BaseModel):
    id: str
    java_ping_record_id: str
    player_id: str
    name: str


class JavaPingRecord(BaseModel):
    id: str
    java_server_id: str
    timeout: float
    is_timeout: bool
    version_protocol: int | None
    version_name: str | None
    latency: float | None
    players_online: int | None
    players_max: int | None
    players_sample: list[JavaPingRecordPlayer] | None
    description: str | None
    favicon: str | None  # Data URL


class JavaPingRecordRepository(ABC):
    @abstractmethod
    def get_latest_java_ping_record(
        self,
        java_server_id: str,
        count: int,
    ) -> list[JavaPingRecord]:
        ...

    @abstractmethod
    def create_java_ping_record(
        self,
        java_server_id: str,
        timeout: float,
        is_timeout: bool,
        version_protocol: int | None,
        version_name: str | None,
        latency: float | None,
        players_online: int | None,
        players_max: int | None,
        players_sample: list[CreateJavaPingRecordJavaPingRecordPlayer] | None,
        description: str | None,
        favicon: str | None,
    ) -> JavaPingRecord:
        ...


class JavaPingRecordRepositoryImpl(JavaPingRecordRepository):
    def __init__(self, database_url: str):
        self.engine = create_engine(url=database_url)

    def get_latest_java_ping_record(
        self,
        java_server_id: str,
        count: int,
    ) -> list[JavaPingRecord]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                sql_text(
                    """
                        SELECT
                            "id",
                            "java_server_id",
                            "timeout",
                            "is_timeout",
                            "version_protocol",
                            "version_name",
                            "latency",
                            "players_online",
                            "players_max",
                            "description",
                            "favicon"
                        FROM "java_ping_records"
                        WHERE
                            "java_server_id" = :java_server_id
                        ORDER BY "created_at" DESC
                        LIMIT :count
                    """,
                ),
                parameters=dict(
                    java_server_id=java_server_id,
                    count=count,
                ),
            ).fetchall()

            return list(
                map(
                    lambda row: JavaPingRecord(
                        id=str(row[0]),
                        java_server_id=str(row[1]),
                        timeout=row[2],
                        is_timeout=row[3],
                        version_protocol=row[4],
                        version_name=row[5],
                        latency=row[6],
                        players_online=row[7],
                        players_max=row[8],
                        description=row[9],
                        favicon=row[10],
                    ),
                    rows,
                ),
            )

    def create_java_ping_record(
        self,
        java_server_id: str,
        timeout: float,
        is_timeout: bool,
        version_protocol: int | None,
        version_name: str | None,
        latency: float | None,
        players_online: int | None,
        players_max: int | None,
        players_sample: list[CreateJavaPingRecordJavaPingRecordPlayer] | None,
        description: str | None,
        favicon: str | None,
    ):
        with self.engine.connect() as conn:
            with conn.begin():
                ping_record_row = conn.execute(
                    sql_text(
                        """
                            INSERT INTO "java_ping_records"(
                                "java_server_id",
                                "timeout",
                                "is_timeout",
                                "version_protocol",
                                "version_name",
                                "latency",
                                "players_online",
                                "players_max",
                                "description",
                                "favicon"
                            ) VALUES(
                                :java_server_id,
                                :timeout,
                                :is_timeout,
                                :version_protocol,
                                :version_name,
                                :latency,
                                :players_online,
                                :players_max,
                                :description,
                                :favicon
                            ) RETURNING id
                        """,
                    ),
                    parameters=dict(
                        java_server_id=java_server_id,
                        timeout=timeout,
                        is_timeout=is_timeout,
                        version_protocol=version_protocol,
                        version_name=version_name,
                        latency=latency,
                        players_online=players_online,
                        players_max=players_max,
                        description=description,
                        favicon=favicon,
                    ),
                ).fetchone()
                ping_record_id = str(ping_record_row[0])

                ret_players_sample: list[JavaPingRecordPlayer] | None = (
                    [] if players_sample is not None else None
                )
                if players_sample is not None:
                    for player_sample in players_sample:
                        ping_record_player_row = conn.execute(
                            sql_text(
                                """
                                    INSERT INTO "java_ping_record_players"(
                                        "java_ping_record_id",
                                        "player_id",
                                        "name"
                                    ) VALUES(
                                        :java_ping_record_id,
                                        :player_id,
                                        :name
                                    ) RETURNING id
                                """,
                            ),
                            parameters=dict(
                                java_ping_record_id=ping_record_id,
                                player_id=player_sample.player_id,
                                name=player_sample.name,
                            ),
                        ).fetchone()
                        ret_players_sample.append(
                            JavaPingRecordPlayer(
                                id=str(ping_record_player_row[0]),
                                java_ping_record_id=ping_record_id,
                                player_id=player_sample.player_id,
                                name=player_sample.name,
                            )
                        )

                return JavaPingRecord(
                    id=ping_record_id,
                    java_server_id=java_server_id,
                    timeout=timeout,
                    is_timeout=is_timeout,
                    version_protocol=version_protocol,
                    version_name=version_name,
                    latency=latency,
                    players_online=players_online,
                    players_max=players_max,
                    players_sample=ret_players_sample,
                    description=description,
                    favicon=favicon,
                )
