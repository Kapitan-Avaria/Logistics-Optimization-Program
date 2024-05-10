from database.db_init import db_init
from database.db_queries import *
from client_1c.http_client_1c import HTTPClient1C
from geocoding.geocoding_wrapper import GeocodingWrapper
from routing.routing_wrapper import RoutingWrapper
from vrp.vrp_wrapper import VRPWrapper
from pathlib import Path


def load_initial_data(client: HTTPClient1C):
    all_products = client.get_all_products()
    insert_products(all_products)

    all_vehicles = client.get_all_vehicles()
    insert_vehicles(all_vehicles)

    archived_orders = client.get_archived_orders()
    insert_orders(archived_orders)

    # all_vehicle_geodata = client1c.get_vehicles_geodata()


def load_operational_data(client: HTTPClient1C):
    # Load available orders to the database
    available_orders = client1c.get_available_orders()
    insert_orders(available_orders)

    # Load available vehicles from 1C
    available_vehicles = client1c.get_available_vehicles()
    insert_vehicles(available_vehicles)
    # TODO: обращение по имени каждой машины, которой ещё нет в базе, добавление в базу


if __name__ == '__main__':
    db_path = Path('..').resolve() / 'database.db'
    url_1c = ''

    # Initialize main clients and wrappers
    client1c = HTTPClient1C(url_1c)
    geocoder = GeocodingWrapper()
    router = RoutingWrapper()
    vrp_solver = VRPWrapper()
    db_is_empty = db_init(db_path)

    # Load historical and utility data from 1C if database was created in the first time
    if db_is_empty:
        load_initial_data(client1c)

    # Load operational data from 1C
    load_operational_data(client1c)

    # Load available orders from the database
    orders = get_objects(class_name=Order, status=0)


    solutions = vrp_solver.run(orders, available_vehicles)


