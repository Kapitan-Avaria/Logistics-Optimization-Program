from json import load


with open("config.cfg", 'r') as f:
    config = load(f)

YANDEX_GEO_API_KEY = config["YANDEX_GEO_API_KEY"]
YANDEX_ROUTING_API_KEY = config["YANDEX_ROUTING_API_KEY"]
ORS_ROUTING_API_KEY = config["ORS_ROUTING_API_KEY"]
