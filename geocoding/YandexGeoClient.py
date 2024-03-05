import requests

from decimal import Decimal


class YandexGeoClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def _request(self, address: str) -> dict:
        response = requests.get(
            "https://geocode-maps.yandex.ru/1.x/",
            params=dict(format="json", apikey=self.api_key, geocode=address, lang='ru_RU', ll='38.957643, 44.987749', spn='20, 20'),
        )

        if response.status_code == 200:
            res = response.json()["response"]
            return res
        elif response.status_code == 400:
            raise Exception(f"400 Bad Request. body={response.content!r}")
        elif response.status_code == 403:
            raise Exception("403 Forbidden. Invalid API-key")
    
    def coordinates(self, address: str) -> tuple:
        data = self._request(address)["GeoObjectCollection"]["featureMember"]

        if not data:
            raise Exception(f'Nothing found for {address}')
        
        coords: str = data[0]["GeoObject"]["Point"]["pos"]
        longitude, latitude = tuple(coords.split(" "))

        return Decimal(longitude), Decimal(latitude)

