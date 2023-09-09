# syntax=docker/dockerfile:1.4
ARG BASE_IMAGE=ubuntu:focal
ARG BASE_RUNTIME_IMAGE=${BASE_IMAGE}

FROM ${BASE_IMAGE} AS python-env

ARG DEBIAN_FRONTEND=noninteractive
ARG PYENV_VERSION=v2.3.26
ARG PYTHON_VERSION=3.11.5

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
ENV PATH=/home/user/.local/bin:/opt/python/bin:${PATH}

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

RUN <<EOF
    set -eu

    groupadd -o -g 1000 user
    useradd -o -m -u 1000 -g user user
EOF


FROM base-env AS bedrock-updater-runtime-env

WORKDIR /work
ADD ./requirements-bedrock-updater.txt /work/
RUN gosu user pip3 install --no-cache-dir -r /work/requirements-bedrock-updater.txt

ADD ./aoirint_mcping_server /work/aoirint_mcping_server
ADD ./aoirint_mcping_server_bedrock_updater.py /work/

ENV MCPING_BEDROCK_UPDATER_LOOP=1

CMD [ "gosu", "user", "python3", "aoirint_mcping_server_bedrock_updater.py" ]


FROM base-env AS java-updater-runtime-env

WORKDIR /work
ADD ./requirements-java-updater.txt /work/
RUN gosu user pip3 install --no-cache-dir -r /work/requirements-java-updater.txt

ADD ./aoirint_mcping_server /work/aoirint_mcping_server
ADD ./aoirint_mcping_server_java_updater.py /work/

ENV MCPING_JAVA_UPDATER_LOOP=1

CMD [ "gosu", "user", "python3", "aoirint_mcping_server_java_updater.py" ]


FROM base-env AS web-api-runtime-env

WORKDIR /work
ADD ./requirements-web-api.txt /work/
RUN gosu user pip3 install --no-cache-dir -r /work/requirements-web-api.txt

ADD ./aoirint_mcping_server /work/aoirint_mcping_server
ADD ./aoirint_mcping_server_web_api.py /work/

ENV MCPING_WEB_API_HOST=0.0.0.0

CMD [ "gosu", "user", "python3", "aoirint_mcping_server_web_api.py" ]
