from pymongo import MongoClient


class DBInterface:

    def __init__(self, connection_string: str):
        self.dbcalc = self._get_database(connection_string)

    def _get_database(self, connection_string: str):
        self.client = MongoClient(connection_string)
        return self.client['calculations']

    def add_calculation_to_clients_record_and_set_id(self, client_ip, expression, result):
        calculations = self.dbcalc[client_ip]
        calculation_id = calculations.count_documents({}) + 1
        calculation = {
            "id": f'{calculation_id}',
            "expression": f"{expression}",
            "result": f"{result}"
        }
        calculations.insert_one(calculation)

        return calculation_id

    def get_all_calculations(self, client_ip):
        calculations = self.dbcalc[client_ip]
        calc_list = list(calculations.find())

        return calc_list

    def get_calculation_by_id(self, client_ip, calc_id):
        calculations = self.dbcalc[client_ip]
        calc_list = list(calculations.find({"id": f"{calc_id}"}))

        return calc_list