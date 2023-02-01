import pytest
from fastapi.testclient import TestClient
from calculator_server.calculations import calculator, Storage


client = TestClient(calculator)


def test_expression_from_valid_json_is_added_to_calculations_record():

    def action():
        response = client.post(
            "/calculations",
            json={"expression": "2+2"}
        )
        return response

    def assertion(response):
        assert response.json() == {"url": "/calculations/1"}

    def teardown():
        storage = Storage()
        storage.calculations = [[], []]

    action_result = action()
    assertion(action_result)
    teardown()


def test_returns_all_calculations_of_given_client():

    def arrangement():
        client.post(
            "/calculations",
            json={"expression": "2+2"}
        )

        client.post(
            "/calculations",
            json={"expression": "2/0"}
        )

        client.post(
            "/calculations",
            json={"expression": "(26-8) / 9"}
        )

    def action():
        response = client.get("/calculations")
        return response

    def assertion(response):
        assert response.json() == [{"id": "1", "expression": "2+2", "result": "4"},
                                   {"id": "2", "expression": "2/0", "result": "Invalid expression (division by zero)."},
                                   {"id": "3", "expression": "(26-8) / 9", "result": "2.0"}]

    def teardown():
        storage = Storage()
        storage.calculations = [[], []]

    arrangement()
    action_result = action()
    assertion(action_result)
    teardown()


def test_returns_calculation_of_given_client_by_id():

    def arrangement():
        client.post(
            "/calculations",
            json={"expression": "2+2"}
        )

        client.post(
            "/calculations",
            json={"expression": "2/0"}
        )

        client.post(
            "/calculations",
            json={"expression": "(26-8) / 9"}
        )

    def action():
        response = client.get("/calculations/2")
        return response

    def assertion(response):
        assert response.json() == [{"id": "2", "expression": "2/0", "result": "Invalid expression (division by zero)."}]

    def teardown():
        storage = Storage()
        storage.calculations = [[], []]

    arrangement()
    action_result = action()
    assertion(action_result)
    teardown()
