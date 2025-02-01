from abc import ABC, abstractmethod


class BusinessDataInterface(ABC):
    @abstractmethod
    def get_available_orders(self, start_date, end_date):
        pass

    @abstractmethod
    def get_depot(self):
        pass

    @abstractmethod
    def get_all_products(self):
        pass

    @abstractmethod
    def get_product_by_id(self, product_id):
        pass

    @abstractmethod
    def get_all_vehicles(self):
        pass

    @abstractmethod
    def get_routes(self, start_date, end_date):
        pass
