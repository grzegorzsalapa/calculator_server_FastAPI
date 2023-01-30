from fastapi import FastAPI, Request
from .calculate import calculate, CalculationError
from pydantic import BaseModel


class Calculation(BaseModel):
    expression: str


class Calculations(BaseModel):
    id: str


calculator = FastAPI()


@calculator.post("/calculations", status_code=201)
def add_calculation(calc: Calculation, request: Request):

    storage = Storage()
    client_ip = request.client.host
    expression = calc.expression

    result = _get_calc_result(expression)

    client_index = _find_client_or_create_new(client_ip, storage.calculations)
    calculation_id = _add_calculation_to_clients_record_and_set_id(client_index, expression, result, storage.calculations)

    return {"url": f'/calculations/{calculation_id}'}


@calculator.get("/calculations", status_code=302)
def get_all_calculations(request: Request):

    storage = Storage()
    client_ip = request.client.host
    try:
        client_index = storage.calculations[0].index(client_ip)

    except ValueError:

        request.code = 302
        request.message = "No records were found."
        request.json_out = ''

        return

    calculations = storage.calculations[1][client_index]

    return _pack_calculations(calculations)


@calculator.get("/calculations/{calc_id}", status_code=302)
def get_calculation_by_id(calc_id: int, request: Request):

    storage = Storage()
    id = calc_id
    client_ip = request.client.host

    try:
        client_index = storage.calculations[0].index(client_ip)

    except ValueError:

        request.code = 404
        request.message = "No records were found."
        request.json_out = ''

        return

    calculation_id = id - 1
    try:
        calculations = [storage.calculations[1][client_index][calculation_id]]

    except IndexError:

        request.code = 404
        request.message = f"Record with id: {request.calculation_id} does not exist."
        request.json_out = ''

        return

    return _pack_calculations(calculations)


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
        payload.append({'id': f'{tup[0]}', 'expression': f'{tup[1]}', 'result': f'{tup[2]}'})
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
