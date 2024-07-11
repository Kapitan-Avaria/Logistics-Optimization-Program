from yandex_geo_client import YandexGeoClient
from source.constants import YANDEX_GEO_API_KEY
from source.database.db_init import Address
from source.database.db_queries import insert_coords, get_objects
from time import sleep


class GeocodingWrapper:

    def __init__(self):
        self.geo_clients = {
            "yandex": YandexGeoClient(YANDEX_GEO_API_KEY)
        }
    
    def get_coordinates(self, address):
        address_object = get_objects(class_name=Address, address_string=address)[0]
        coords = (float(address_object['longitude']), float(address_object['latitude'])) \
            if (address_object['longitude'] is not None and address_object['latitude'] is not None) \
            else None

        if coords is None:
            coords = self.geo_clients["yandex"].get_coordinates(address)
            insert_coords(address, coords)

        return coords

    def geocode_bulk(self, addresses, time_interval_seconds=1):
        for address in addresses:
            coords = self.get_coordinates(address)
            sleep(time_interval_seconds)

