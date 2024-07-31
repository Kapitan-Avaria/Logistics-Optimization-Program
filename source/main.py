from database.db_init import db_init

from client_1c.http_client_1c import HTTPClient1C
from geocoding.geocoding_wrapper import GeocodingWrapper
from routing.routing_wrapper import RoutingWrapper
from vrp.vrp_wrapper import VRPWrapper
from pathlib import Path


if __name__ == '__main__':
    db_path = Path('..').resolve() / 'database.db'
    url_1c = ''

    # Initialize main clients and wrappers
    client1c = HTTPClient1C(url_1c)
    geocoder = GeocodingWrapper()
    router = RoutingWrapper()
    vrp_solver = VRPWrapper()
    db_is_empty = db_init(db_path)




