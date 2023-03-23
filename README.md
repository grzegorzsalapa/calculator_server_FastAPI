# Calculator server (FastAPI)

Simple server based on FastAPI framework, calculating well-formed math equations. Intended to use with "
calculator_client_http".
Server stores expressions and results in MongoDB. Service is monitored with use of Prometheus and Grafana. All elements
of this service are set up in separate docker containers.

## How to run

#### Running containers with docker compose

It is necessary to install Docker and Docker Compose prior to running command below. Versions verified are v23.0.1 and
v2.16.0 respectively.

    $  docker compose up -d

Server is running on port 8080, does not require authenticating and can be accessed with "
calculator_client_http" app or by valid REST API request (check docs/openapi.json).

## How to test

#### Installation

    $ pip install .[test]

#### Run tests

    $ pytest

## Requirements

All packages required to run calculator module are specified in pyproject.toml file.
