from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text


class BedrockServer(BaseModel):
    id: str
    name: str
    host: str
    port: int


class BedrockServerApiModel(ABC):
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


class BedrockServerApiModelImpl(BedrockServerApiModel):
    def __init__(self, database_url: str):
        self.engine = create_engine(url=database_url)

    def get_bedrock_servers(self) -> list[BedrockServer]:
        with self.engine.connect() as conn:
            row = conn.execute(
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
            ).fetchone()

            if row is None:
                return None

            return BedrockServer(
                id=row["id"],
                name=row["name"],
                host=row["host"],
                port=row["port"],
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
