import os
import time
from pathlib import Path

import schedule
import yaml
from pydantic import BaseModel, parse_obj_as
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text

from ..api.bedrock_ping_api import BedrockPingApiModelImpl, BedrockPingTimeoutError
from ..api.bedrock_ping_record_api import BedrockPingRecordApiModelImpl
from ..api.bedrock_server_api import BedrockServerApiModelImpl


class UpdaterConfig(BaseModel):
    interval: float
    timeout: float
    database_url: str | None


async def update(config: UpdaterConfig) -> None:
    bedrock_server_api = BedrockServerApiModelImpl(database_url=config.database_url)
    bedrock_ping_api = BedrockPingApiModelImpl()
    bedrock_ping_record_api = BedrockPingRecordApiModelImpl(
        database_url=config.database_url
    )

    for bedrock_server in bedrock_server_api.get_bedrock_servers():
        try:
            ping_result = bedrock_ping_api.ping(
                host=bedrock_server.host,
                port=bedrock_server.port,
                timeout=config.timeout,
            )
            bedrock_ping_record_api.create_bedrock_ping_record(
                bedrock_server_id=bedrock_server.id,
                timeout=config.timeout,
                is_timeout=False,
                version_protocol=ping_result.version_protocol,
                version_brand=ping_result.version_brand,
                version_version=ping_result.version_version,
                players_online=ping_result.players_online,
                players_max=ping_result.players_max,
                motd=ping_result.motd,
                map=ping_result.map,
                gamemode=ping_result.gamemode,
            )
        except BedrockPingTimeoutError:
            bedrock_ping_record_api.create_bedrock_ping_record(
                bedrock_server_id=bedrock_server.id,
                timeout=config.timeout,
                is_timeout=True,
                version_protocol=None,
                version_brand=None,
                version_version=None,
                players_online=None,
                players_max=None,
                motd=None,
                map=None,
                gamemode=None,
            )


async def update_loop(config: UpdaterConfig) -> None:
    schedule.every(interval=config.interval).seconds.do(update, config=config)

    while True:
        schedule.run_pending()
        time.sleep(0.1)


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--updater_config_file",
        type=Path,
        default=os.environ.get("MCPING_UPDATER_CONFIG_FILE", "updater_config.yaml"),
    )
    parser.add_argument(
        "--database_url",
        type=str,
        default=os.environ.get("MCPING_UPDATER_DATABASE_URL", "sqlite3://db.sqlite3"),
    )
    parser.add_argument(
        "-l",
        "--loop",
        action="store_true",
    )
    args = parser.parse_args()

    config_file: Path = args.config_file
    database_url: str = args.database_url
    loop: bool = args.loop

    with config_file.open(mode="r", encoding="utf-8") as fp:
        config = parse_obj_as(UpdaterConfig, yaml.safe_load(fp))

    if database_url is not None:
        config.database_url = args.database_url

    if loop:
        await update_loop()
    else:
        await update()
