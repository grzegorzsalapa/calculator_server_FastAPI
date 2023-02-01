from fastapi import FastAPI, Request, HTTPException
from .calculate import calculate, CalculationError
from pydantic import BaseModel
import logging


logging.basicConfig(
    filename='logs/server.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)


calculator = FastAPI()


class Calculation(BaseModel):
    expression: str


class Calculations(BaseModel):
    id: str


@calculator.post("/calculations", status_code=201)
def add_calculation(calc: Calculation, request: Request):

    try:
        storage = Storage()
        client_ip = request.client.host
        expression = calc.expression

        result = _get_calc_result(expression)

        client_index = _find_client_or_create_new(client_ip, storage.calculations)
        calculation_id = _add_calculation_to_clients_record_and_set_id(
            client_index,
            expression,
            result,
            storage.calculations
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
        storage = Storage()
        client_ip = request.client.host
        try:
            client_index = storage.calculations[0].index(client_ip)

        except ValueError:

            raise HTTPException(status_code=404,
                                detail="No records were found.",
                                headers={"X-Error": "No records were found."})

        calculations = storage.calculations[1][client_index]

        logging.info(f'Request from {client_ip} | {len(calculations)} record(s) returned.')

        return _pack_calculations(calculations)

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
        storage = Storage()
        client_ip = request.client.host
        calculation_id = calc_id - 1

        try:
            client_index = storage.calculations[0].index(client_ip)

        except ValueError:

            logging.info(f"Request from {client_ip} | No records of this client were found.")
            raise HTTPException(status_code=404,
                                detail="Record not found.",
                                headers={"X-Error": "Record not found."})

        try:
            calculations = [storage.calculations[1][client_index][calculation_id]]

        except IndexError:

            logging.info(f'Request from {client_ip} | No record with id {calc_id} was found.')
            raise HTTPException(status_code=404,
                                detail=f"Record with id: {calc_id} was not found.",
                                headers={"X-Error": f"Record with id: {calc_id} was not found."})

        return _pack_calculations(calculations)

    except HTTPException:
        raise

    except Exception as e:

        logging.error(f"Error while processing request from {client_ip} |", str(e))
        raise HTTPException(status_code=500,
                            detail=str(e),
                            headers={"X-Error": "Unexpected error."})


def _find_client_or_create_new(client_ip, calculations):

    try:
        client_index = calculations[0].index(client_ip)
    except ValueError:
        client_index = len(calculations[0])
        calculations[0].append(client_ip)
        calculations[1].append([])

    return client_index


def _add_calculation_to_clients_record_and_set_id(client_index, expression, result, calculations):

    calculation_id = len(calculations[1][client_index]) + 1
    calculations[1][client_index].append((calculation_id, expression, result))

    return calculation_id


def _get_calc_result(expression):

    try:
        result = str(calculate(expression))
    except CalculationError as e:
        result = str(e)

    return result


def _pack_calculations(calculations):

    payload = []
    i = 1
    for tup in calculations:
        payload.append({"id": f'{tup[0]}', "expression": f"{tup[1]}", "result": f"{tup[2]}"})
        i += 1

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
