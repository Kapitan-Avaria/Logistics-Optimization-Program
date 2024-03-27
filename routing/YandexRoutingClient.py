import requests
from routing_utils import unix_time_from_hour, get_unix_time_now


class YandexRoutingClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def _request(self, origins, destinations, departure_time) -> dict:
        response = requests.get(
            "https://api.routing.yandex.net/v2/distancematrix/",
            params=dict(format="json",
                        apikey=self.api_key,
                        origins=origins,
                        destinations=destinations,
                        mode="truck",
                        departure_time=departure_time),
        )

        if response.status_code == 200:
            res = response.json()["rows"]
            return res
        elif response.status_code == 400:
            raise Exception(f"400: Запрос не содержит одного или нескольких обязательных параметров. body={response.content!r}")
        elif response.status_code == 401:
            raise Exception("403: Запрос не содержит параметр apikey или указан неверный ключ")
        elif response.status_code == 429:
            raise Exception("429: Слишком много запросов")
        elif response.status_code == 500:
            raise Exception("500: Системная ошибка сервера. Повторите запрос с небольшой задержкой.")
        elif response.status_code == 504:
            raise Exception("504: Системная ошибка сервера. Повторите запрос с небольшой задержкой.")


    def get_segments_data(self, origins: list[tuple[str, str]], destinations: list[tuple[str, str]], departure_hour: str = None):
        origins = '|'.join(map(','.join, origins))
        destinations = '|'.join(map(','.join, destinations))

        if departure_hour is not None:
            departure_time = unix_time_from_hour(hour=departure_hour)
        else:
            departure_time = get_unix_time_now()

        data = self._request(origins, destinations, departure_time)
        res = dict()

        for i in range(len(data)):
            for j, segment in enumerate(data[i]):

                if segment["status"] != "OK":
                    continue    # Заменить на сохранение ошибок в логи

                res[(i, j)] = {
                    "distance": int(segment["distance"]["value"]),
                    "duration": int(segment["duration"]["value"])
                }
        return res

