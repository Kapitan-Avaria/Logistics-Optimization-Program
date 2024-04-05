from YandexGeoClient import YandexGeoClient
from source.constants import YANDEX_GEO_API_KEY
from source.database.db_sessions import get_coords_from_db_address, insert_coords, read_strings_input


class GeocodingInterface:

    geo_clients = {
        "yandex": YandexGeoClient(YANDEX_GEO_API_KEY)
    }
    
    def get_coords_from_addresses(self, address):
        coords = get_coords_from_db_address(address_string=address)

        if coords is None:
            lon, lat = self.geo_clients["yandex"].get_coordinates(address)
            coords = (lat, lon)
            insert_coords(address, coords)

        return coords

    def geocode_bulk(self, addresses):
        for address in addresses:
            coords = self.get_coords_from_addresses(address)


gi = GeocodingInterface()
gi.geocode_bulk(read_strings_input())
