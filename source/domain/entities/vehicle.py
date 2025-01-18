from dataclasses import dataclass


@dataclass
class Vehicle:
    id: int
    name: str
    category: str
    dimensions: dict
    weight_capacity: int
