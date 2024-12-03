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
    def get_java_servers(self) -> list[JavaServer]: ...

    @abstractmethod
    def create_java_server(
        self,
        name: str,
        host: str,
        port: int,
    ) -> JavaServer: ...

    @abstractmethod
    def update_java_server(
        self,
        id: str,
        name: str,
        host: str,
        port: int,
    ) -> JavaServer: ...

    @abstractmethod
    def delete_java_server(
        self,
        id: str,
    ) -> str: ...


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
                    parameters={
                        "name": name,
                        "host": host,
                        "port": port,
                    },
                ).fetchone()

                if row is None:
                    raise Exception("Failed to create a record of java_servers")

                return JavaServer(
                    id=str(row[0]),
                    name=name,
                    host=host,
                    port=port,
                )

    def update_java_server(
        self,
        id: str,
        name: str,
        host: str,
        port: int,
    ) -> JavaServer:
        with self.engine.connect() as conn:
            with conn.begin():
                rows = conn.execute(
                    sql_text(
                        """
                            UPDATE "java_servers"
                            SET
                                "name" = :name,
                                "host" = :host,
                                "port" = :port
                            WHERE
                                "id" = :id
                            RETURNING "id"
                        """,
                    ),
                    parameters={
                        "id": id,
                        "name": name,
                        "host": host,
                        "port": port,
                    },
                ).fetchall()

                if len(rows) != 1:
                    raise Exception(f"Failed to update java_server (id={id})")

                return JavaServer(
                    id=id,
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
                    parameters={
                        "id": id,
                    },
                )

                return id
