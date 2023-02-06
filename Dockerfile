# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY calculator_server calculator_server
COPY logs logs
CMD ["uvicorn", "calculator_server.calculations:calculator", "--host", "0.0.0.0", "--port", "8080"]
