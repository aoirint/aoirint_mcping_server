# aoirint_mcping

## Migration

This repository uses [golang-migrate](https://github.com/golang-migrate/migrate).

To apply the migrations,

```shell
docker compose run --rm migrate -path=/migrations -database="postgres://postgres:postgres_password@postgres:5432/postgres?sslmode=disable" up
```

## Library management

This repository uses [Poetry](https://github.com/python-poetry/poetry).

To dump `requirements*.txt`,

```shell
poetry export --without-hashes --with web -o requirements-web.txt
poetry export --without-hashes --with updater -o requirements-updater.txt
poetry export --without-hashes --with dev,web,updater -o requirements-dev.txt
```
