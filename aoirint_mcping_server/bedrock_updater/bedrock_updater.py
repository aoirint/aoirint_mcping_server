import logging
import os
import time

import schedule
from pydantic import BaseModel

from .. import __version__ as APP_VERSION
from ..lib.repository.bedrock_ping_record_repository import (
    BedrockPingRecordRepositoryImpl,
)
from ..lib.repository.bedrock_ping_repository import (
    BedrockPingRefusedError,
    BedrockPingRepositoryImpl,
    BedrockPingTimeoutError,
)
from ..lib.repository.bedrock_server_repository import BedrockServerRepositoryImpl
from ..lib.util.logging_utility import setup_logger

logger = logging.Logger(name="bedrock_updater")


class BedrockUpdaterConfig(BaseModel):
    database_url: str
    interval: int
    timeout: float


def update(config: BedrockUpdaterConfig) -> None:
    bedrock_server_api = BedrockServerRepositoryImpl(database_url=config.database_url)
    bedrock_ping_api = BedrockPingRepositoryImpl()
    bedrock_ping_record_api = BedrockPingRecordRepositoryImpl(
        database_url=config.database_url
    )

    for bedrock_server in bedrock_server_api.get_bedrock_servers():
        logger.info(
            f"Ping {bedrock_server.host}:{bedrock_server.port} ({bedrock_server.id})"
        )
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
                is_refused=False,
                version_protocol=ping_result.version_protocol,
                version_brand=ping_result.version_brand,
                version_version=ping_result.version_version,
                latency=ping_result.latency,
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
                is_refused=False,
                version_protocol=None,
                version_brand=None,
                version_version=None,
                latency=None,
                players_online=None,
                players_max=None,
                motd=None,
                map=None,
                gamemode=None,
            )
        except BedrockPingRefusedError:
            bedrock_ping_record_api.create_bedrock_ping_record(
                bedrock_server_id=bedrock_server.id,
                timeout=config.timeout,
                is_timeout=False,
                is_refused=True,
                version_protocol=None,
                version_brand=None,
                version_version=None,
                latency=None,
                players_online=None,
                players_max=None,
                motd=None,
                map=None,
                gamemode=None,
            )


def update_loop(config: BedrockUpdaterConfig) -> None:
    schedule.every(interval=config.interval).seconds.do(update, config=config)

    while True:
        schedule.run_pending()
        time.sleep(1)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database_url",
        type=str,
        default=os.environ.get("MCPING_BEDROCK_UPDATER_DATABASE_URL"),
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=os.environ.get("MCPING_BEDROCK_UPDATER_INTERVAL", "300"),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=os.environ.get("MCPING_BEDROCK_UPDATER_TIMEOUT", "3"),
    )
    parser.add_argument(
        "-l",
        "--loop",
        action="store_true",
        default=os.environ.get("MCPING_BEDROCK_UPDATER_LOOP") == "1",
    )
    parser.add_argument(
        "--log_level",
        type=int,
        default=os.environ.get("MCPING_BEDROCK_UPDATER_LOG_LEVEL", logging.INFO),
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default=os.environ.get("MCPING_BEDROCK_UPDATER_LOG_FILE"),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {APP_VERSION}"
    )
    args = parser.parse_args()

    log_level: int = args.log_level
    log_file: str | None = args.log_file
    database_url: str = args.database_url
    interval: int = args.interval
    timeout: float = args.timeout
    loop: bool = args.loop

    logging.basicConfig(
        level=log_level,
    )
    setup_logger(logger=logger, log_level=log_level, log_file=log_file)

    config = BedrockUpdaterConfig(
        database_url=database_url,
        interval=interval,
        timeout=timeout,
    )

    if loop:
        update_loop(config=config)
    else:
        update(config=config)
