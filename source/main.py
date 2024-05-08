from database.db_init import db_init
from database.db_queries import *
from client_1c.http_client_1c import HTTPClient1C
from geocoding.geocoding_wrapper import GeocodingWrapper
from routing.routing_wrapper import RoutingWrapper
from vrp.vrp_wrapper import VRPWrapper
from pathlib import Path


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
    db_path = Path().resolve() / 'database.db'
    url_1c = ''

    db_init(db_path)
    first_data_load(url_1c)

    geocoder = GeocodingWrapper()
    router = RoutingWrapper()
    vrp_solver = VRPWrapper(url_1c)

