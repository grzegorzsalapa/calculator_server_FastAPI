import pytest
from fastapi.testclient import TestClient
# from starlette.testclient import TestClient
from calculator_server.calculations import calculator


client = TestClient(calculator)


def test_expression_from_valid_json_is_added_to_calculations_record():

    response = client.post(
        "/calculations",
        json={"expression": "2+2"}
    )

    assert response.json() == {"url": "/calculations/1"}


def test_returns_all_calculations_of_given_client():

    response = client.get("/calculations")

    assert response.json() == '[{"id": "1", "expression": "2+2", "result": "4"}, ' \
                               '{"id": "2", "expression": "2/0", "result": "Invalid expression (division by zero)."}, ' \
                               '{"id": "3", "expression": "(26-8) / 9", "result": "2.0"}]'


def test_returns_calculation_of_given_client_by_id():

    response = client.get("/calculations/2")

    assert response.json() == '[{"id": "2", "expression": "2/0", "result": "Invalid expression (division by zero)."}]'
