import json
from pathlib import Path


class Config:
    YANDEX_GEO_API_KEY: str
    YANDEX_ROUTING_API_KEY: str
    ORS_ROUTING_API_KEY: str
    DB_PATH: Path
    URL_1C: str
    DEPOT_ADDRESS: str

    DEFAULT_SHIFT_START_B: str
    DEFAULT_SHIFT_START_C: str
    DEFAULT_SHIFT_DURATION_B: str
    DEFAULT_SHIFT_DURATION_C: str
    ALLOW_OVERNIGHT_ROUTES_B: bool
    ALLOW_OVERNIGHT_ROUTES_C: bool
    ACTUAL_VOLUME_RATIO: float

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        path = Path('').resolve()
        if (path / 'source').exists():
            path = path / 'source'
        else:
            while path.name != 'source':
                path = path.parent
        self.path = path
        self.load()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        with open(self.path / "config.cfg", 'r+', encoding='utf8') as f:
            data = json.load(f)
            if key not in data.keys():
                return
            if data[key] == value:
                return
            data[key] = value
            f.seek(0)
            new_data = json.dumps(data, indent=2)
            f.write(new_data)
            f.truncate()

    def load(self):
        with open(self.path / "config.cfg", 'r', encoding='utf8') as f:
            config = json.load(f)

        self.YANDEX_GEO_API_KEY: str = config["YANDEX_GEO_API_KEY"]
        self.YANDEX_ROUTING_API_KEY: str = config["YANDEX_ROUTING_API_KEY"]
        self.ORS_ROUTING_API_KEY: str = config["ORS_ROUTING_API_KEY"]
        self.DB_PATH = Path(config["DB_PATH"])
        self.URL_1C: str = config["URL_1C"]
        self.DEPOT_ADDRESS: str = config["DEPOT_ADDRESS"]

        self.DEFAULT_SHIFT_START_B: str = config["DEFAULT_SHIFT_START_B"]
        self.DEFAULT_SHIFT_START_C: str = config["DEFAULT_SHIFT_START_C"]
        self.DEFAULT_SHIFT_DURATION_B: str = config["DEFAULT_SHIFT_DURATION_B"]
        self.DEFAULT_SHIFT_DURATION_C: str = config["DEFAULT_SHIFT_DURATION_C"]
        self.ALLOW_OVERNIGHT_ROUTES_B: bool = config["ALLOW_OVERNIGHT_ROUTES_B"]
        self.ALLOW_OVERNIGHT_ROUTES_C: bool = config["ALLOW_OVERNIGHT_ROUTES_C"]
        self.ACTUAL_VOLUME_RATIO: float = config["ACTUAL_VOLUME_RATIO"]

