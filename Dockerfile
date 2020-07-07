FROM python:3.8-slim-buster
MAINTAINER "CasperLabs, LLC. <info@casperlabs.io>"

USER root
WORKDIR /opt/docker

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ protobuf-compiler make \
    && apt-get clean

ENTRYPOINT ["casperlabs_client"]

# COPY and run pip install before other source, so cached with src changes.
COPY requirements.txt /src/requirements.txt
RUN cd /src \
    && pip install -r requirements.txt

COPY . /src

RUN cd /src \
    && python setup.py sdist \
    && python -m pip install dist/casperlabs_client* \
    && pytest tests
