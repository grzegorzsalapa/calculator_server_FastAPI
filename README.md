# Calculator server (FastAPI)

Simple server based on FastAPI framework, calculating well-formed math equations. Intended to use with "
calculator_client_http".
Server stores expressions and results in MongoDB. Service is monitored with use of Prometheus and Grafana. All elements
of this service are set up in separate docker containers.

## How to run

#### Running containers with docker compose

    $  docker compose up -d

## How to test

#### Installation

    $ pip install .[test]

#### Run tests

    $ pytest

## Requirements

All packages required to run calculator module are specified in pyproject.toml file.
