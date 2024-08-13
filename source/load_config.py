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
DEPOT_ADDRESS: str = config["DEPOT_ADDRESS"]

DEFAULT_SHIFT_START_B: str = config["DEFAULT_SHIFT_START_B"]
DEFAULT_SHIFT_START_C: str = config["DEFAULT_SHIFT_START_C"]
DEFAULT_SHIFT_DURATION_B: str = config["DEFAULT_SHIFT_DURATION_B"]
DEFAULT_SHIFT_DURATION_C: str = config["DEFAULT_SHIFT_DURATION_C"]
ALLOW_OVERNIGHT_ROUTES_B: bool = config["ALLOW_OVERNIGHT_ROUTES_B"]
ALLOW_OVERNIGHT_ROUTES_C: bool = config["ALLOW_OVERNIGHT_ROUTES_C"]
