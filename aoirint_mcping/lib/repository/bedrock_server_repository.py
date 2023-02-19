from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text


class BedrockServer(BaseModel):
    id: str
    name: str
    host: str
    port: int


class BedrockServerRepository(ABC):
    @abstractmethod
    def get_bedrock_servers(self) -> list[BedrockServer]:
        ...

    @abstractmethod
    def create_bedrock_server(
        self,
        name: str,
        host: str,
        port: int,
    ) -> BedrockServer:
        ...


class BedrockServerRepositoryImpl(BedrockServerRepository):
    def __init__(self, database_url: str):
        self.engine = create_engine(url=database_url)

    def get_bedrock_servers(self) -> list[BedrockServer]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                sql_text(
                    """
                        SELECT
                            "id",
                            "name",
                            "host",
                            "port"
                        FROM "bedrock_servers"
                        ORDER BY "created_at" ASC
                    """,
                ),
            ).fetchall()

            return list(
                map(
                    lambda row: BedrockServer(
                        id=str(row[0]),
                        name=row[1],
                        host=row[2],
                        port=row[3],
                    ),
                    rows,
                )
            )

    def create_bedrock_server(
        self,
        name: str,
        host: str,
        port: int,
    ) -> BedrockServer:
        with self.engine.connect() as conn:
            with conn.begin():
                row = conn.execute(
                    sql_text(
                        """
                            INSERT INTO "bedrock_servers"(
                                "name",
                                "host",
                                "port"
                            ) VALUES(
                                :name,
                                :host,
                                :port
                            ) RETURNING id
                        """,
                    ),
                    parameters=dict(
                        name=name,
                        host=host,
                        port=port,
                    ),
                ).fetchone()

                return BedrockServer(
                    id=str(row[0]),
                    name=name,
                    host=host,
                    port=port,
                )
