from database.db_init import *
from database.db_queries import *
from Client1C.http_client_1c import HTTPClient1C
from geocoding.geocoding_interface import GeocodingInterface


def first_data_load(url):
    client1c = HTTPClient1C(url)

    all_products = client1c.get_all_products()
    insert_products(all_products)

    all_vehicles = client1c.get_all_vehicles()
    insert_vehicles(all_vehicles)

    archived_orders = client1c.get_archived_orders()
    insert_orders(archived_orders)

    # all_vehicle_geodata = client1c.get_vehicles_geodata()


if __name__ == '__main__':
    url_1c = ''
    first_data_load(url_1c)

