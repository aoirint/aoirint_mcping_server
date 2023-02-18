import os
import time

import schedule
from pydantic import BaseModel

from ..api.bedrock_ping_api import BedrockPingApiModelImpl, BedrockPingTimeoutError
from ..api.bedrock_ping_record_api import BedrockPingRecordApiModelImpl
from ..api.bedrock_server_api import BedrockServerApiModelImpl


class UpdaterConfig(BaseModel):
    database_url: str
    interval: float
    timeout: float


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
        "--database_url",
        type=str,
        default=os.environ.get("MCPING_UPDATER_DATABASE_URL"),
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=os.environ.get("MCPING_UPDATER_INTERVAL"),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=os.environ.get("MCPING_UPDATER_TIMEOUT"),
    )
    parser.add_argument(
        "-l",
        "--loop",
        action="store_true",
        default=os.environ.get("MCPING_UPDATER_LOOP") == "1",
    )
    args = parser.parse_args()

    database_url: str = args.database_url
    interval: float = args.interval
    timeout: float = args.timeout
    loop: bool = args.loop

    config = UpdaterConfig(
        database_url=database_url,
        interval=interval,
        timeout=timeout,
    )

    if loop:
        await update_loop(config=config)
    else:
        await update(config=config)
