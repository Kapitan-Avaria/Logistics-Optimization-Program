from source.domain.data_business_interface import BusinessDataInterface
from source.domain.database_interface import DatabaseInterface


class DataOperator:
    def __init__(self, db: DatabaseInterface, business_data: BusinessDataInterface):
        self.db = db
        self.business_data = business_data

    def load_from_business_to_db(self):
        all_products = self.business_data.get_all_products()
        all_vehicles = self.business_data.get_all_vehicles()
        available_orders = self.business_data.get_available_orders()

