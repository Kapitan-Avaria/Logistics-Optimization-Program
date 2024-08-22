import json
from pathlib import Path


class Config:
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

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        with open(self.path / "config.cfg", 'r+', encoding='utf8') as f:
            config = json.load(f)
            if key not in config.keys():
                return
            if config[key] == value:
                return
            config[key] = value
            f.seek(0)
            new_config = json.dumps(config, indent=2)
            f.write(new_config)
            f.truncate()

    def __getattr__(self, item):
        with open(self.path / "config.cfg", 'r', encoding='utf8') as f:
            config = json.load(f)
            if item not in config.keys():
                raise AttributeError(f"Config has no attribute '{item}'")
            return config[item]

