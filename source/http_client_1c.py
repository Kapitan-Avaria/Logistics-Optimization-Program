import requests


class HTTPClient1C:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def safe_request(request_func):
        def wrapper(*args, **kwargs):
            try:
                return request_func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                print(f"Connection error: Can't connect to 1C HTTP-service via {request_func.__name__} method")
                return {}
        return wrapper

    def is_available(self):
        # TODO: remake to authorisation in future
        try:
            requests.get(self.url)
            return True
        except requests.exceptions.ConnectionError:
            print(f"Connection error: Can't connect to 1C HTTP-service")
            return False

    @safe_request
    def get_archived_orders(self):
        return requests.get(self.url + '/get_archived_orders').json()["orders"]

    @safe_request
    def get_available_orders(self):
        return requests.get(self.url + '/get_available_orders').json()["orders"]

    @safe_request
    def get_depot(self, depot_id):
        return requests.get(self.url + f'/get_depot/{depot_id}').json()

    @safe_request
    def get_all_products(self):
        return requests.get(self.url + '/get_all_products').json()["products"]

    @safe_request
    def get_product_by_name(self, name):
        return requests.get(self.url + f'/get_product/{name}').json()["products"]

    @safe_request
    def get_product_by_id(self, id):
        return requests.get(self.url + f'/get_product_by_id/{id}').json()["products"]

    @safe_request
    def get_all_vehicles(self):
        return requests.get(self.url + '/get_all_vehicles').json()["vehicles"]

    @safe_request
    def get_vehicle(self, name):
        return requests.get(self.url + f'/get_vehicle/{name}').json()["vehicles"]

    @safe_request
    def get_available_vehicles(self):
        return requests.get(self.url + '/get_available_vehicles').json()["vehicles"]

    @safe_request
    def get_vehicles_geodata(self, date):
        return requests.get(self.url + f'/get_geodata/{date}').json()["data"]
