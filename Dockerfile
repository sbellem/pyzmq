FROM python:3.8.2-alpine3.11

ENV PYTHONUNBUFFERED=1

RUN apk add --update --no-cache \
  gcc \
  g++ \
  musl-dev \
  libffi-dev \
  openssl-dev \
  zeromq-dev

RUN apk add --update --no-cache vim

WORKDIR /usr/src/pyzmq

COPY dev-requirements.txt ./
RUN pip install --no-cache-dir -r dev-requirements.txt

COPY . .

RUN pip install --editable .
