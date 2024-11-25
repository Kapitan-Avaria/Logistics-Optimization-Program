import json
from pathlib import Path
import sys
import os


class Config:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)

        self.path = resource_path('data/config.cfg')
        self.path_loc = resource_path('data/config_loc_ru.cfg')

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        with open(self.path, 'r+', encoding='utf8') as f:
            config = json.load(f)
            if key not in config.keys():
                return
            if config[key] == value:
                return
            config[key] = value
            f.seek(0)
            new_config = json.dumps(config, ensure_ascii=False, indent=2)
            f.write(new_config)
            f.truncate()

    def __getattr__(self, item):
        config = self.load_dict()
        if item not in config.keys():
            raise AttributeError(f"Config has no attribute '{item}'")
        return config[item]

    def load_dict(self):
        with open(self.path, 'r', encoding='utf8') as f:
            config = json.load(f)
            return config

    def load_dict_loc(self):
        with open(self.path_loc, 'r', encoding='utf8') as f:
            config_loc = json.load(f)
            return config_loc
