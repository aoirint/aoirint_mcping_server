from pathlib import Path

import yaml
from pydantic import BaseModel, parse_obj_as


class ServerItem(BaseModel):
    key: str
    type: str
    name: str
    host: str
    port: int


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--servers_file", type=Path, required=True)
    args = parser.parse_args()

    servers_file: Path = args.servers_file

    with servers_file.open(mode="r", encoding="utf-8") as fp:
        servers = parse_obj_as(list[ServerItem], yaml.safe_load(fp))

    print(servers)
