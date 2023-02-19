import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from ..lib.repository.bedrock_ping_record_repository import (
    BedrockPingRecord,
    BedrockPingRecordRepositoryImpl,
)
from ..lib.repository.bedrock_server_repository import (
    BedrockServer,
    BedrockServerRepositoryImpl,
)


class WebApiConfig(BaseModel):
    host: str
    port: int
    reload: bool
    database_url: str


def create_asgi_app(config: WebApiConfig):
    app = FastAPI()

    @app.post("/bedrock_server/list", response_model=list[BedrockServer])
    async def bedrock_server_list():
        bedrock_server_api = BedrockServerRepositoryImpl(
            database_url=config.database_url
        )
        return bedrock_server_api.get_bedrock_servers()

    @app.post("/bedrock_server/create", response_model=BedrockServer)
    async def bedrock_server_create(
        name: str,
        host: str,
        port: int,
    ):
        bedrock_server_api = BedrockServerRepositoryImpl(
            database_url=config.database_url
        )
        return bedrock_server_api.create_bedrock_server(
            name=name,
            host=host,
            port=port,
        )

    @app.post("/bedrock_ping_record/latest", response_model=list[BedrockPingRecord])
    async def bedrock_ping_record_latest(
        bedrock_server_id: str,
        count: int = 5,
    ):
        if count > 20:
            raise Exception('"count" must be less than or equal to 100')

        bedrock_ping_record_api = BedrockPingRecordRepositoryImpl(
            database_url=config.database_url
        )

        return bedrock_ping_record_api.get_latest_bedrock_ping_record(
            bedrock_server_id=bedrock_server_id,
            count=count,
        )

    return app


def web_api_loop(config: WebApiConfig):
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
    args = parser.parse_args()

    database_url: str = args.database_url
    host: str = args.host
    port: int = args.port
    reload: bool = args.reload

    config = WebApiConfig(
        host=host,
        port=port,
        reload=reload,
        database_url=database_url,
    )

    web_api_loop(config=config)