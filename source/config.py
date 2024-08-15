from json import load
from pathlib import Path


class Config:
    YANDEX_GEO_API_KEY: str
    YANDEX_ROUTING_API_KEY: str
    ORS_ROUTING_API_KEY: str
    DB_PATH: Path
    DEPOT_ADDRESS: str

    DEFAULT_SHIFT_START_B: str
    DEFAULT_SHIFT_START_C: str
    DEFAULT_SHIFT_DURATION_B: str
    DEFAULT_SHIFT_DURATION_C: str
    ALLOW_OVERNIGHT_ROUTES_B: bool
    ALLOW_OVERNIGHT_ROUTES_C: bool

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.load()

    def load(self):
        path = Path('').resolve()
        if (path / 'source').exists():
            path = path / 'source'
        else:
            while path.name != 'source':
                path = path.parent

        with open(path / "config.cfg", 'r', encoding='utf8') as f:
            config = load(f)

        self.YANDEX_GEO_API_KEY: str = config["YANDEX_GEO_API_KEY"]
        self.YANDEX_ROUTING_API_KEY: str = config["YANDEX_ROUTING_API_KEY"]
        self.ORS_ROUTING_API_KEY: str = config["ORS_ROUTING_API_KEY"]
        self.DB_PATH = Path(config["DB_PATH"])
        self.DEPOT_ADDRESS: str = config["DEPOT_ADDRESS"]

        self.DEFAULT_SHIFT_START_B: str = config["DEFAULT_SHIFT_START_B"]
        self.DEFAULT_SHIFT_START_C: str = config["DEFAULT_SHIFT_START_C"]
        self.DEFAULT_SHIFT_DURATION_B: str = config["DEFAULT_SHIFT_DURATION_B"]
        self.DEFAULT_SHIFT_DURATION_C: str = config["DEFAULT_SHIFT_DURATION_C"]
        self.ALLOW_OVERNIGHT_ROUTES_B: bool = config["ALLOW_OVERNIGHT_ROUTES_B"]
        self.ALLOW_OVERNIGHT_ROUTES_C: bool = config["ALLOW_OVERNIGHT_ROUTES_C"]

