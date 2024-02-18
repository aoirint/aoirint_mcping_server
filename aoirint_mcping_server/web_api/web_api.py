import logging
import os

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .. import __version__ as APP_VERSION
from ..lib.repository.bedrock_ping_record_repository import (
    BedrockPingRecord,
    BedrockPingRecordRepositoryImpl,
)
from ..lib.repository.bedrock_server_repository import (
    BedrockServer,
    BedrockServerRepositoryImpl,
)
from ..lib.repository.java_ping_record_repository import (
    JavaPingRecord,
    JavaPingRecordRepositoryImpl,
)
from ..lib.repository.java_server_repository import JavaServer, JavaServerRepositoryImpl
from ..lib.util.logging_utility import setup_logger

logger = logging.Logger(name="web_api")

FASTAPI_HEADER_NONE: str | None = Header(None)


class WebApiConfig(BaseModel):
    host: str
    port: int
    reload: bool
    read_api_key: str | None
    write_api_key: str | None
    max_latest_count: int
    database_url: str


def create_asgi_app(config: WebApiConfig) -> FastAPI:
    app = FastAPI()

    async def verify_read_api_key(
        x_read_api_key: str | None = FASTAPI_HEADER_NONE,
    ) -> str | None:
        # If config.read_api_key is not defined, everyone can read.
        if config.read_api_key is None or config.read_api_key == "":
            return x_read_api_key

        if x_read_api_key != config.read_api_key:
            raise HTTPException(status_code=400, detail="X-Read-Api-Key header invalid")
        return x_read_api_key

    async def verify_write_api_key(
        x_write_api_key: str | None = FASTAPI_HEADER_NONE,
    ) -> str | None:
        # If config.write_api_key is not defined, everyone can write.
        if config.write_api_key is None or config.write_api_key == "":
            return x_write_api_key

        if x_write_api_key != config.write_api_key:
            raise HTTPException(
                status_code=400, detail="X-Write-Api-Key header invalid"
            )
        return x_write_api_key

    @app.post(
        "/bedrock_server/list",
        response_model=list[BedrockServer],
        dependencies=[Depends(verify_read_api_key)],
    )
    async def bedrock_server_list() -> list[BedrockServer]:
        bedrock_server_api = BedrockServerRepositoryImpl(
            database_url=config.database_url
        )
        return bedrock_server_api.get_bedrock_servers()

    @app.post(
        "/bedrock_server/create",
        response_model=BedrockServer,
        dependencies=[Depends(verify_write_api_key)],
    )
    async def bedrock_server_create(
        name: str,
        host: str,
        port: int,
    ) -> BedrockServer:
        bedrock_server_api = BedrockServerRepositoryImpl(
            database_url=config.database_url
        )
        return bedrock_server_api.create_bedrock_server(
            name=name,
            host=host,
            port=port,
        )

    @app.post(
        "/bedrock_server/update",
        response_model=BedrockServer,
        dependencies=[Depends(verify_write_api_key)],
    )
    async def bedrock_server_update(
        id: str,
        name: str,
        host: str,
        port: int,
    ) -> BedrockServer:
        bedrock_server_api = BedrockServerRepositoryImpl(
            database_url=config.database_url
        )
        return bedrock_server_api.update_bedrock_server(
            id=id,
            name=name,
            host=host,
            port=port,
        )

    class DeleteBedrockServerResponse(BaseModel):
        id: str

    @app.post(
        "/bedrock_server/delete",
        response_model=DeleteBedrockServerResponse,
        dependencies=[Depends(verify_write_api_key)],
    )
    async def bedrock_server_delete(
        id: str,
    ) -> DeleteBedrockServerResponse:
        bedrock_server_api = BedrockServerRepositoryImpl(
            database_url=config.database_url
        )
        return DeleteBedrockServerResponse(
            id=bedrock_server_api.delete_bedrock_server(
                id=id,
            ),
        )

    @app.post(
        "/bedrock_ping_record/latest",
        response_model=list[BedrockPingRecord],
        dependencies=[Depends(verify_read_api_key)],
    )
    async def bedrock_ping_record_latest(
        bedrock_server_id: str,
        count: int = 5,
    ) -> list[BedrockPingRecord]:
        if count > config.max_latest_count:
            raise Exception(
                f'"count" must be less than or equal to {config.max_latest_count}'
            )

        bedrock_ping_record_api = BedrockPingRecordRepositoryImpl(
            database_url=config.database_url
        )

        return bedrock_ping_record_api.get_latest_bedrock_ping_record(
            bedrock_server_id=bedrock_server_id,
            count=count,
        )

    @app.post(
        "/java_server/list",
        response_model=list[JavaServer],
        dependencies=[Depends(verify_read_api_key)],
    )
    async def java_server_list() -> list[JavaServer]:
        java_server_api = JavaServerRepositoryImpl(database_url=config.database_url)
        return java_server_api.get_java_servers()

    @app.post(
        "/java_server/create",
        response_model=JavaServer,
        dependencies=[Depends(verify_write_api_key)],
    )
    async def java_server_create(
        name: str,
        host: str,
        port: int,
    ) -> JavaServer:
        java_server_api = JavaServerRepositoryImpl(database_url=config.database_url)
        return java_server_api.create_java_server(
            name=name,
            host=host,
            port=port,
        )

    @app.post(
        "/java_server/update",
        response_model=JavaServer,
        dependencies=[Depends(verify_write_api_key)],
    )
    async def java_server_update(
        id: str,
        name: str,
        host: str,
        port: int,
    ) -> JavaServer:
        java_server_api = JavaServerRepositoryImpl(database_url=config.database_url)
        return java_server_api.update_java_server(
            id=id,
            name=name,
            host=host,
            port=port,
        )

    class DeleteJavaServerResponse(BaseModel):
        id: str

    @app.post(
        "/java_server/delete",
        response_model=DeleteJavaServerResponse,
        dependencies=[Depends(verify_write_api_key)],
    )
    async def java_server_delete(
        id: str,
    ) -> DeleteJavaServerResponse:
        java_server_api = JavaServerRepositoryImpl(database_url=config.database_url)
        return DeleteJavaServerResponse(
            id=java_server_api.delete_java_server(
                id=id,
            )
        )

    @app.post(
        "/java_ping_record/latest",
        response_model=list[JavaPingRecord],
        dependencies=[Depends(verify_read_api_key)],
    )
    async def java_ping_record_latest(
        java_server_id: str,
        count: int = 5,
    ) -> list[JavaPingRecord]:
        if count > config.max_latest_count:
            raise Exception(
                f'"count" must be less than or equal to {config.max_latest_count}'
            )

        java_ping_record_api = JavaPingRecordRepositoryImpl(
            database_url=config.database_url
        )

        return java_ping_record_api.get_latest_java_ping_record(
            java_server_id=java_server_id,
            count=count,
        )

    return app


def web_api_loop(config: WebApiConfig) -> None:
    uvicorn.run(
        create_asgi_app(config=config),
        host=config.host,
        port=config.port,
        reload=config.reload,
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database_url",
        type=str,
        default=os.environ.get("MCPING_WEB_API_DATABASE_URL"),
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCPING_WEB_API_HOST", "0.0.0.0"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=os.environ.get("MCPING_WEB_API_PORT", "5000"),
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=os.environ.get("MCPING_WEB_API_RELOAD") == "1",
    )
    parser.add_argument(
        "--read_api_key",
        type=str,
        default=os.environ.get("MCPING_WEB_API_READ_API_KEY"),
    )
    parser.add_argument(
        "--write_api_key",
        type=str,
        default=os.environ.get("MCPING_WEB_API_WRITE_API_KEY"),
    )
    parser.add_argument(
        "--max_latest_count",
        type=int,
        default=os.environ.get("MCPING_WEB_API_MAX_LATEST_COUNT", "20"),
    )
    parser.add_argument(
        "--log_level",
        type=int,
        default=os.environ.get("MCPING_WEB_API_LOG_LEVEL", logging.INFO),
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default=os.environ.get("MCPING_WEB_API_LOG_FILE"),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {APP_VERSION}"
    )
    args = parser.parse_args()

    log_level: int = args.log_level
    log_file: str | None = args.log_file
    database_url: str = args.database_url
    host: str = args.host
    port: int = args.port
    reload: bool = args.reload
    read_api_key: str | None = args.read_api_key
    write_api_key: str | None = args.write_api_key
    max_latest_count: int = args.max_latest_count

    logging.basicConfig(
        level=log_level,
    )
    setup_logger(logger=logger, log_level=log_level, log_file=log_file)

    config = WebApiConfig(
        host=host,
        port=port,
        reload=reload,
        read_api_key=read_api_key,
        write_api_key=write_api_key,
        max_latest_count=max_latest_count,
        database_url=database_url,
    )

    web_api_loop(config=config)
