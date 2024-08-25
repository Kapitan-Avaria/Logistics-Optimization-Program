from yandex_geo_client import YandexGeoClient
from config import Config
from db_init import Address
from db_queries import insert_coords, get_objects
from time import sleep


class GeocodingWrapper:

    def __init__(self):
        self.geo_clients = {
            "yandex": YandexGeoClient(Config().YANDEX_GEO_API_KEY)
        }
    
    def get_coordinates(self, string_address, time_sleep_seconds=1):
        # Get the address object from the db
        address_object = get_objects(class_name=Address, string_address=string_address)[0]
        # Get coords from address if exist
        coords = (float(address_object['longitude']), float(address_object['latitude'])) \
            if (address_object['longitude'] is not None and address_object['latitude'] is not None) \
            else None

        # Get coords from geocoder only if there are no coords in the address
        if coords is None:
            coords = self.geo_clients["yandex"].get_coordinates(string_address)
            sleep(time_sleep_seconds)

        return coords

    def geocode_bulk(self, addresses, time_sleep_seconds=1):
        for address_string in addresses:
            coords = self.get_coordinates(address_string, time_sleep_seconds)
            insert_coords(address_string, coords)

