# Calculator server

Calculator is a REST API server based on FastAPI. It can calculate simple, well-formed mathematical expressions.

Calculator stores expressions and results in MongoDB database, from which they can be retrieved by id. Calculator
server is monitored with use of Prometheus from which data is sent to Grafana.

There is a simple client application (calculator_client_http) to access Calculator server.

### Example of use

##### calculator

    >>> result = calculator('(2 + 2) * 2')

#### pycalculator_CLI

    $ cli

### Requirements

All packages required to run calculator module are specified in requirements.txt file.