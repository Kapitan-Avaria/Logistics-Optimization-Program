from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    form_factor: str
    dimensions: dict
    volume: float
