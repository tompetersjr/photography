FROM python:3.6-stretch

RUN apt-get update
RUN apt-get -y dist-upgrade
RUN apt-get -y install exiftool

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /srv/photos
COPY . /srv/photos
WORKDIR /srv/photos

RUN python3 -m venv /srv/env
RUN /srv/env/bin/pip install --upgrade pip setuptools wheel
RUN /srv/env/bin/pip install -e ".[testing]"

# A simple script to wait for other docker images to be started while using docker-compose
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.0.0/wait /usr/bin/wait
RUN chmod +x /usr/bin/wait

ADD ./scripts/initenviroment.sh /usr/bin/initenviroment.sh
RUN chmod +x /usr/bin/initenviroment.sh

ADD ./scripts/serve.sh /usr/bin/serve.sh
RUN chmod +x /usr/bin/serve.sh

ADD ./scripts/celeryworker.sh /usr/bin/celeryworker.sh
RUN chmod +x /usr/bin/celeryworker.sh

ADD ./scripts/celerybeat.sh /usr/bin/celerybeat.sh
RUN chmod +x /usr/bin/celerybeat.sh
