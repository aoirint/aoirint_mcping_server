import os
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI
from pydantic import BaseModel, parse_obj_as

from ..api.bedrock_ping_record_api import (
    BedrockPingRecord,
    BedrockPingRecordApiModelImpl,
)
from ..api.bedrock_server_api import BedrockServer, BedrockServerApiModelImpl


class WebConfig(BaseModel):
    host: str
    port: int
    reload: bool
    database_url: str | None


async def create_asgi_app(config: WebConfig):
    app = FastAPI()

    @app.post("/bedrock_server/list", response_model=list[BedrockServer])
    async def bedrock_server_list():
        bedrock_server_api = BedrockServerApiModelImpl(database_url=config.database_url)
        return bedrock_server_api.get_bedrock_servers()

    class CreateBedrockServerRequestBody(BaseModel):
        name: str
        host: str
        port: int

    @app.post("/bedrock_server/create", response_model=BedrockServer)
    async def bedrock_server_create(server: CreateBedrockServerRequestBody):
        bedrock_server_api = BedrockServerApiModelImpl(database_url=config.database_url)
        return bedrock_server_api.create_bedrock_server(
            name=server.name,
            host=server.host,
            port=server.port,
        )

    class LatestBedrockPingRecordRequestBody(BaseModel):
        bedrock_server_id: str

    @app.post("/bedrock_ping_record/latest", response_model=BedrockPingRecord)
    async def bedrock_ping_record_latest(params: LatestBedrockPingRecordRequestBody):
        bedrock_ping_record_api = BedrockPingRecordApiModelImpl(
            database_url=config.database_url
        )
        return bedrock_ping_record_api.get_latest_bedrock_ping_record(
            bedrock_server_id=params.bedrock_server_id
        )

    return app


async def web_server_loop(config: WebConfig):
    uvicorn.run(
        create_asgi_app(),
        host=config.host,
        port=config.port,
        reload=config.reload,
    )


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--web_config_file",
        type=Path,
        default=os.environ.get("MCPING_WEB_CONFIG_FILE", "web_config.yaml"),
    )
    parser.add_argument(
        "--database_url",
        type=str,
        default=os.environ.get("MCPING_WEB_DATABASE_URL", "sqlite3://db.sqlite3"),
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCPING_WEB_HOST", "0.0.0.0"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=os.environ.get("MCPING_WEB_PORT", "5000"),
    )
    parser.add_argument(
        "--reload",
        action="store_true",
    )
    args = parser.parse_args()

    config_file: Path = args.config_file
    database_url: str = args.database_url

    with config_file.open(mode="r", encoding="utf-8") as fp:
        config = parse_obj_as(WebConfig, yaml.safe_load(fp))

    if database_url is not None:
        config.database_url = args.database_url

    await web_server_loop()
