# syntax=docker/dockerfile:1.4
FROM python:3.10 AS base-env

RUN <<EOF
    apt-get update
    apt-get install -y \
        gosu
    apt-get clean
    rm -rf /var/apt/lists/*
EOF

RUN <<EOF
    groupadd -o -g 1000 user
    useradd -o -m -u 1000 -g user user
EOF


FROM base-env AS updater-runtime-env

WORKDIR /work
ADD ./requirements-updater.txt /work/
RUN gosu user pip3 install --no-cache-dir -r /work/requirements-updater.txt

ADD ./aoirint_mcping /work/aoirint_mcping
ADD ./aoirint_mcping_updater.py /work/

CMD [ "gosu", "user", "python3", "aoirint_mcping_updater.py" ]


FROM base-env AS web-runtime-env

WORKDIR /work
ADD ./requirements-web.txt /work/
RUN gosu user pip3 install --no-cache-dir -r /work/requirements-web.txt

ADD ./aoirint_mcping /work/aoirint_mcping
ADD ./aoirint_mcping_web.py /work/

CMD [ "gosu", "user", "python3", "aoirint_mcping_web.py" ]
