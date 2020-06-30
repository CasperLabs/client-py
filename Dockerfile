FROM python:3.8-slim-buster
MAINTAINER joe@casperlabs.io


RUN apt-get update \
    && apt-get install -y g++ protobuf-compiler \
    && apt-get clean

# TODO: Install of protobuf-compiler above is 3.6, test to see if this works or if we need the latest version built below
#RUN apt-get install autoconf automake libtool curl make
#ARG PROTOBUF_VERSION=3.12.3
#RUN mkdir -p /protobuf \
#    && curl -L https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOBUF_VERSION}/protobuf-python-${PROTOBUF_VERSION}.tar.gz | tar xvz -C /protobuf --strip-components=1 \
#    && cd /protobuf \
#    && autoreconf -f -i -Wall,no-obsolete \
#    && ./configure --prefix=/usr --enable-static=no \
#    && make -j4 \
#    && make install \
#    && cd .. \
#    && rm -rf /protobuf

ENTRYPOINT ["casperlabs_client"]

# COPY and run pip install before other source, so cached with src changes.
COPY requirements.txt /src/requirements.txt
RUN cd /src \
    && pip install -r requirements.txt

# Don't need g++ after requirements install.
# Saves about 60 MB
RUN apt-get remove -y g++ \
    && apt-get autoremove -y


COPY . /src

RUN cd /src \
    && python setup.py sdist \
    && ./install.sh \
    && pytest tests \
    && rm -rf dist casperlabs_client.egg-info casperlabs_client/proto .eggs .pytest_cache
