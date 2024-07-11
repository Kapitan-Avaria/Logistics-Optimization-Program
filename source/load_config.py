from json import load
from pathlib import Path


path = Path('').resolve()
while path.name != 'source':
    path = path.parent

with open(path / "config.cfg", 'r', encoding='utf8') as f:
    config = load(f)

YANDEX_GEO_API_KEY: str = config["YANDEX_GEO_API_KEY"]
YANDEX_ROUTING_API_KEY: str = config["YANDEX_ROUTING_API_KEY"]
ORS_ROUTING_API_KEY: str = config["ORS_ROUTING_API_KEY"]
DB_PATH = Path(config["DB_PATH"])
