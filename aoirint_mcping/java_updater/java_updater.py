import logging
import os
import time

import schedule
from pydantic import BaseModel

from ..lib.repository.java_ping_record_repository import (
    CreateJavaPingRecordJavaPingRecordPlayer,
    JavaPingRecordRepositoryImpl,
)
from ..lib.repository.java_ping_repository import (
    JavaPingRepositoryImpl,
    JavaPingTimeoutError,
)
from ..lib.repository.java_server_repository import JavaServerRepositoryImpl
from ..lib.util.logging_utility import setup_logging_format_time_with_timezone

logger = logging.Logger(name="java_updater")


class JavaUpdaterConfig(BaseModel):
    database_url: str
    interval: float
    timeout: float


def update(config: JavaUpdaterConfig) -> None:
    java_server_api = JavaServerRepositoryImpl(database_url=config.database_url)
    java_ping_api = JavaPingRepositoryImpl()
    java_ping_record_api = JavaPingRecordRepositoryImpl(
        database_url=config.database_url
    )

    for java_server in java_server_api.get_java_servers():
        logger.info(f"Ping {java_server.host}:{java_server.port} ({java_server.id})")
        try:
            ping_result = java_ping_api.ping(
                host=java_server.host,
                port=java_server.port,
                timeout=config.timeout,
            )
            java_ping_record_api.create_java_ping_record(
                java_server_id=java_server.id,
                timeout=config.timeout,
                is_timeout=False,
                version_protocol=ping_result.version_protocol,
                version_name=ping_result.version_name,
                latency=ping_result.latency,
                players_online=ping_result.players_online,
                players_max=ping_result.players_max,
                players_sample=list(
                    map(
                        lambda player_sample: CreateJavaPingRecordJavaPingRecordPlayer(
                            player_id=player_sample.id,
                            name=player_sample.name,
                        ),
                        ping_result.players_sample,
                    )
                ),
                description=ping_result.description,
                favicon=ping_result.favicon,
            )
        except JavaPingTimeoutError:
            java_ping_record_api.create_java_ping_record(
                java_server_id=java_server.id,
                timeout=config.timeout,
                is_timeout=True,
                version_protocol=None,
                version_name=None,
                latency=None,
                players_online=None,
                players_max=None,
                players_sample=None,
                description=None,
                favicon=None,
            )


def update_loop(config: JavaUpdaterConfig) -> None:
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
        default=os.environ.get("MCPING_JAVA_UPDATER_DATABASE_URL"),
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=os.environ.get("MCPING_JAVA_UPDATER_INTERVAL", "300"),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=os.environ.get("MCPING_JAVA_UPDATER_TIMEOUT", "3"),
    )
    parser.add_argument(
        "-l",
        "--loop",
        action="store_true",
        default=os.environ.get("MCPING_JAVA_UPDATER_LOOP") == "1",
    )
    parser.add_argument(
        "--log_level",
        type=int,
        default=os.environ.get("MCPING_JAVA_UPDATER_LOG_LEVEL", logging.INFO),
    )
    args = parser.parse_args()

    log_level: int = args.log_level
    database_url: str = args.database_url
    interval: float = args.interval
    timeout: float = args.timeout
    loop: bool = args.loop

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    setup_logging_format_time_with_timezone()

    config = JavaUpdaterConfig(
        database_url=database_url,
        interval=interval,
        timeout=timeout,
    )

    if loop:
        update_loop(config=config)
    else:
        update(config=config)
