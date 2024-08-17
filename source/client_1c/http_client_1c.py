import requests


class HTTPClient1C:
    def __init__(self, url):
        """url: [ip-address]/[name-of-publication]"""
        self.url = url + '/hs/'

    @staticmethod
    def safe_request(request_func):
        def wrapper(*args, **kwargs):
            try:
                return request_func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                print(f"Connection error: Can't connect to 1C HTTP-service via {request_func.__name__}")
                return {}
        return wrapper

    @safe_request
    def get_archived_orders(self):
        return requests.get(self.url + 'orders/get_archived_orders').json()["orders"]

    @safe_request
    def get_available_orders(self):
        return requests.get(self.url + 'orders/get_available_orders').json()["orders"]

    @safe_request
    def get_all_products(self):
        return requests.get(self.url + 'products/get_all_products').json()["products"]

    @safe_request
    def get_product(self, name):
        return requests.get(self.url + f'products/get_product/{name}').json()["products"]

    @safe_request
    def get_all_vehicles(self):
        return requests.get(self.url + 'vehicles/get_all_vehicles').json()["vehicles"]

    @safe_request
    def get_vehicle(self, name):
        return requests.get(self.url + f'vehicles/get_vehicle/{name}').json()["vehicles"]

    @safe_request
    def get_available_vehicles(self):
        return requests.get(self.url + 'vehicles/get_available_vehicles').json()["vehicles"]

    @safe_request
    def get_vehicles_geodata(self, date):
        return requests.get(self.url + f'vehicles/get_geodata/{date}').json()["data"]

