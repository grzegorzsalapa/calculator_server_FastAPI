import pytest
from fastapi.testclient import TestClient
from calculator_server.calculations import calculator
from unittest.mock import MagicMock, patch


client = TestClient(calculator)


def _set_up_mocked_DB(id_when_added=None, list_with_all=None, list_with_given_id=None):

    db_interface = MagicMock(name="InterfaceInstance")
    db_interface.add_calculation_to_clients_record_and_set_id = MagicMock(return_value=id_when_added)
    db_interface.get_all_calculations = MagicMock(return_value=list_with_all)
    db_interface.get_calculation_by_id = MagicMock(return_value=list_with_given_id)

    return db_interface


def test_expression_from_valid_json_is_added_to_calculations_record_and_result_url_returned():

    def arrangement():
        return _set_up_mocked_DB(id_when_added=3)

    def action():
        response = client.post(
            "/calculations",
            json={"expression": "2+2"}
        )
        return response

    def assertion(response):
        assert response.status_code == 201
        assert response.json() == {"url": "/calculations/3"}

    db_interface_mock = arrangement()
    with patch('calculator_server.calculations.db_interface', new=db_interface_mock):
        action_result = action()
        assertion(action_result)


def test_returns_all_calculations_of_given_client():

    def arrangement():
        return _set_up_mocked_DB(
            list_with_all=[
                {
                    "id": "1",
                    "expression": "2+2",
                    "result": "4"
                },
                {
                    "id": "2",
                    "expression": "2/0",
                    "result": "Invalid expression (division by zero)."
                },
                {
                    "id": "3",
                    "expression": "(26-8) / 9",
                    "result": "2.0"
                }
            ]
        )

    def action():
        response = client.get("/calculations")
        return response

    def assertion(response):
        assert response.status_code == 302
        assert response.json() == [{"id": "1", "expression": "2+2", "result": "4"},
                                   {"id": "2", "expression": "2/0", "result": "Invalid expression (division by zero)."},
                                   {"id": "3", "expression": "(26-8) / 9", "result": "2.0"}]

    db_interface_mock = arrangement()
    with patch('calculator_server.calculations.db_interface', new=db_interface_mock):
        action_result = action()
        assertion(action_result)


def test_returns_calculation_of_given_client_by_id():

    def arrangement():
        return _set_up_mocked_DB(
            list_with_given_id=[
                {
                    "id": "8",
                    "expression": "2/0",
                    "result": "Invalid expression (division by zero)."
                }
            ]
        )

    def action():
        response = client.get("/calculations/8")
        return response

    def assertion(response):
        assert response.status_code == 302
        assert response.json() == [{"id": "2", "expression": "2/0", "result": "Invalid expression (division by zero)."}]

    db_interface_mock = arrangement()
    with patch('calculator_server.calculations.db_interface', new=db_interface_mock):
        action_result = action()
        assertion(action_result)


def test_responds_with_404_when_no_records():

    def arrangement():
        return _set_up_mocked_DB(list_with_all=[{}])

    def action():
        response = client.get("/calculations")
        return response

    def assertion(response):
        assert response.status_code == 404
        assert response.json() == {'detail': 'No records were found.'}

    db_interface_mock = arrangement()
    with patch('calculator_server.calculations.db_interface', new=db_interface_mock):
        action_result = action()
        assertion(action_result)


def test_responds_with_404_when_no_record_with_requested_id():

    def arrangement():
        return _set_up_mocked_DB(list_with_given_id=[{}])

    def action():
        response = client.get("/calculations/5")
        return response

    def assertion(response):
        assert response.status_code == 404
        assert response.json() == {'detail': 'Record not found.'}

    db_interface_mock = arrangement()
    with patch('calculator_server.calculations.db_interface', new=db_interface_mock):
        action_result = action()
        assertion(action_result)
