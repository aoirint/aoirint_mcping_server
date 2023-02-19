from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text


class JavaServer(BaseModel):
    id: str
    name: str
    host: str
    port: int


class JavaServerRepository(ABC):
    @abstractmethod
    def get_java_servers(self) -> list[JavaServer]:
        ...

    @abstractmethod
    def create_java_server(
        self,
        name: str,
        host: str,
        port: int,
    ) -> JavaServer:
        ...

    @abstractmethod
    def delete_java_server(
        self,
        id: str,
    ) -> str:
        ...


class JavaServerRepositoryImpl(JavaServerRepository):
    def __init__(self, database_url: str):
        self.engine = create_engine(url=database_url)

    def get_java_servers(self) -> list[JavaServer]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                sql_text(
                    """
                        SELECT
                            "id",
                            "name",
                            "host",
                            "port"
                        FROM "java_servers"
                        ORDER BY "created_at" ASC
                    """,
                ),
            ).fetchall()

            return list(
                map(
                    lambda row: JavaServer(
                        id=str(row[0]),
                        name=row[1],
                        host=row[2],
                        port=row[3],
                    ),
                    rows,
                )
            )

    def create_java_server(
        self,
        name: str,
        host: str,
        port: int,
    ) -> JavaServer:
        with self.engine.connect() as conn:
            with conn.begin():
                row = conn.execute(
                    sql_text(
                        """
                            INSERT INTO "java_servers"(
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

                return JavaServer(
                    id=str(row[0]),
                    name=name,
                    host=host,
                    port=port,
                )

    def delete_java_server(
        self,
        id: str,
    ) -> str:
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    sql_text(
                        """
                            DELETE FROM "java_servers"
                            WHERE id=:id
                        """,
                    ),
                    parameters=dict(
                        id=id,
                    ),
                )

                return id
