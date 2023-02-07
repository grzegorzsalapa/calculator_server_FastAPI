from fastapi import FastAPI, Request, HTTPException
from starlette_prometheus import metrics, PrometheusMiddleware
from .calculate import calculate, CalculationError
from pydantic import BaseModel
from pymongo import MongoClient
import logging
import time


logging.basicConfig(
    filename='logs/server.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)


def log_processing_time(f):
    def timer(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start_time
        logging.info(f"Request took {duration} to process.")
        return result
    return timer


def get_database():
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)
    return client['calculations']


calculator = FastAPI()
calculator.add_middleware(PrometheusMiddleware)
calculator.add_route("/metrics", metrics)
dbcalc = get_database()


class Calculation(BaseModel):
    expression: str


class Calculations(BaseModel):
    id: str


@calculator.post("/calculations", status_code=201)
def add_calculation(calc: Calculation, request: Request):

    try:
        client_ip = request.client.host
        expression = calc.expression

        result = _get_calc_result(expression)

        calculation_id = _add_calculation_to_clients_record_and_set_id(
            client_ip,
            expression,
            result,
        )

        logging.info(f"Request from {client_ip} | Calculation added with id: {calculation_id}")

        return {'url': f'/calculations/{calculation_id}'}

    except Exception as e:
        logging.error(f"Error while processing request from {client_ip} |", str(e))
        raise HTTPException(status_code=500,
                            detail=str(e),
                            headers={"X-Error": "Unexpected error."})


@calculator.get("/calculations", status_code=302)
def get_all_calculations(request: Request):

    try:
        client_ip = request.client.host
        calculations = dbcalc[client_ip]
        calc_list = list(calculations.find())
        if not calc_list:
            raise HTTPException(status_code=404,
                                detail="No records were found.",
                                headers={"X-Error": "No records were found."})

        logging.info(f'Request from {client_ip} | {len(calc_list)} record(s) returned.')

        return _pack_calculations(calc_list)

    except HTTPException:
        raise

    except Exception as e:

        logging.error(f"Error while processing request from {client_ip} |", str(e))
        raise HTTPException(status_code=500,
                            detail=str(e),
                            headers={"X-Error": "Unexpected error."})


@calculator.get("/calculations/{calc_id}", status_code=302)
def get_calculation_by_id(calc_id: int, request: Request):

    try:
        client_ip = request.client.host

        # try:
        #     client_index = storage.calculations[0].index(client_ip)
        #
        # except ValueError:
        #
        #     logging.info(f"Request from {client_ip} | No records of this client were found.")
        #     raise HTTPException(status_code=404,
        #                         detail="Record not found.",
        #                         headers={"X-Error": "Record not found."})

        # try:
        #     calculations = [storage.calculations[1][client_index][calculation_id]]
        #
        # except IndexError:
        #
        #     logging.info(f'Request from {client_ip} | No record with id {calc_id} was found.')
        #     raise HTTPException(status_code=404,
        #                         detail=f"Record with id: {calc_id} was not found.",
        #                         headers={"X-Error": f"Record with id: {calc_id} was not found."})

        calculations = dbcalc[client_ip]
        calc_list = list(calculations.find({"id": f"{calc_id}"}))

        return _pack_calculations(calc_list)

    except HTTPException:
        raise

    except Exception as e:

        logging.error(f"Error while processing request from {client_ip} |", str(e))
        raise HTTPException(status_code=500,
                            detail=str(e),
                            headers={"X-Error": "Unexpected error."})


def _add_calculation_to_clients_record_and_set_id(client_ip, expression, result):

    calculations = dbcalc[client_ip]
    calculation_id = calculations.count_documents({}) + 1
    calculation = {
        "id": f'{calculation_id}',
        "expression": f"{expression}",
        "result": f"{result}"
    }
    calculations.insert_one(calculation)

    return calculation_id


def _get_calc_result(expression):

    try:
        result = str(calculate(expression))
    except CalculationError as e:
        result = str(e)

    return result


def _pack_calculations(calculations):

    for item in calculations:
        del item["_id"]
    payload = calculations

    return payload


class SingletonMeta(type):  # TODO: Ripped off. Need to understand what's going on...

    _instances = {}

    def __call__(cls, *args, **kwargs):

        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Storage(metaclass=SingletonMeta):

    def __init__(self):
        self.calculations = [[], []]
        logging.info("Storage for calculations created.")
