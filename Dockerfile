# syntax=docker/dockerfile:1.6
ARG BASE_IMAGE=ubuntu:20.04
ARG BASE_RUNTIME_IMAGE=${BASE_IMAGE}

FROM ${BASE_IMAGE} AS python-env

ARG DEBIAN_FRONTEND=noninteractive
ARG PYENV_VERSION=v2.3.36
ARG PYTHON_VERSION=3.11.8

RUN <<EOF
    set -eu

    apt-get update

    apt-get install -y \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        curl \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
        git

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    set -eu

    git clone https://github.com/pyenv/pyenv.git /opt/pyenv
    cd /opt/pyenv
    git checkout "${PYENV_VERSION}"

    PREFIX=/opt/python-build /opt/pyenv/plugins/python-build/install.sh
    /opt/python-build/bin/python-build -v "${PYTHON_VERSION}" /opt/python

    rm -rf /opt/python-build /opt/pyenv
EOF


FROM ${BASE_RUNTIME_IMAGE} AS base-env

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH=/code/aoirint_mcping_server/.venv/bin:/home/user/.local/bin:/opt/python/bin:${PATH}

COPY --from=python-env /opt/python /opt/python

RUN <<EOF
    set -eu

    apt-get update
    apt-get install -y \
        openssl \
        gosu
    apt-get clean
    rm -rf /var/apt/lists/*
EOF

ARG CONTAINER_UID=1000
ARG CONTAINER_GID=1000
RUN <<EOF
    set -eu

    groupadd --non-unique --gid "${CONTAINER_GID}" user
    useradd --non-unique --uid "${CONTAINER_UID}" --gid "${CONTAINER_GID}" --create-home user
EOF

ARG POETRY_VERSION=1.7.1
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"

    gosu user poetry config virtualenvs.in-project true

    mkdir -p /home/user/.cache/pypoetry/{cache,artifacts}
    chown -R "${CONTAINER_UID}:${CONTAINER_GID}" /home/user/.cache
EOF

RUN <<EOF
    set -eu

    mkdir -p /code/aoirint_mcping_server
    chown -R "${CONTAINER_UID}:${CONTAINER_GID}" /code/aoirint_mcping_server
EOF

WORKDIR /code/aoirint_mcping_server


FROM base-env AS bedrock-updater-runtime-env

ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./pyproject.toml ./poetry.lock /code/aoirint_mcping_server/
RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --no-root --with bedrock-updater
EOF

ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./aoirint_mcping_server /code/aoirint_mcping_server/aoirint_mcping_server
ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./aoirint_mcping_server_bedrock_updater.py ./README.md /code/aoirint_mcping_server/
RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --with bedrock-updater
EOF

ENV MCPING_BEDROCK_UPDATER_LOOP=1

CMD [ "gosu", "user", "poetry", "run", "python", "aoirint_mcping_server_bedrock_updater.py" ]


FROM base-env AS java-updater-runtime-env

ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./pyproject.toml ./poetry.lock /code/aoirint_mcping_server/
RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --no-root --with java-updater
EOF

ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./aoirint_mcping_server /code/aoirint_mcping_server/aoirint_mcping_server
ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./aoirint_mcping_server_java_updater.py ./README.md /code/aoirint_mcping_server/
RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --with java-updater
EOF

ENV MCPING_JAVA_UPDATER_LOOP=1

CMD [ "gosu", "user", "poetry", "run", "python", "aoirint_mcping_server_java_updater.py" ]


FROM base-env AS web-api-runtime-env

ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./pyproject.toml ./poetry.lock /code/aoirint_mcping_server/
RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --no-root --with web-api
EOF

ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./aoirint_mcping_server /code/aoirint_mcping_server/aoirint_mcping_server
ADD --chown="${CONTAINER_UID}:${CONTAINER_GID}" ./aoirint_mcping_server_web_api.py ./README.md /code/aoirint_mcping_server/
RUN --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid="${CONTAINER_UID}",gid="${CONTAINER_GID}",target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --with web-api
EOF

ENV MCPING_WEB_API_HOST=0.0.0.0

CMD [ "gosu", "user", "poetry", "run", "python", "aoirint_mcping_server_web_api.py" ]
