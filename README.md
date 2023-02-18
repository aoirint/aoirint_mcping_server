# aoirint_mcping

```
docker compose run --rm migrate -path=/migrations -database="postgres://postgres:postgres_password@postgres:5432/postgres?sslmode=disable" up
```

```shell
poetry export --without-hashes --with web -o requirements-web.txt
poetry export --without-hashes --with updater -o requirements-updater.txt
poetry export --without-hashes --with dev,web,updater -o requirements-dev.txt
```
