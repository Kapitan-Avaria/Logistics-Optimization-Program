import requests


class HTTPClient1C:
    def __init__(self, url):
        """url: [ip-address]/[name-of-publication]"""
        self.url = url + '/hs/'

    def get_archived_orders(self):
        return requests.get(self.url + 'orders/get_archived_orders')

    def get_available_orders(self):
        return requests.get(self.url + 'orders/get_available_orders')

    def get_all_products(self):
        return requests.get(self.url + 'products/get_all_products')

    def get_product_by_name(self, name):
        return requests.get(self.url + f'products/get_product_by_name/{name}')

    def get_all_vehicles(self):
        return requests.get(self.url + 'vehicles/get_all_vehicles')

    def get_vehicle(self, name):
        return requests.get(self.url + f'vehicles/get_vehicle/{name}')

    def get_available_vehicles(self):
        return requests.get(self.url + 'vehicles/get_available_vehicles')

    def get_vehicles_geodata(self, date):
        return requests.get(self.url + f'vehicles/get_geodata/{date}')


