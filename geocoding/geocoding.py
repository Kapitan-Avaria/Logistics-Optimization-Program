from YandexClient import Client
from constants import YANDEX_API_KEY

client = Client(YANDEX_API_KEY)
coords = client.coordinates("Кореновск г., Гагарина ул., 11")
print(coords)