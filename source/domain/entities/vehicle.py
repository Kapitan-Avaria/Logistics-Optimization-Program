from dataclasses import dataclass


@dataclass
class Vehicle:
    id: int
    name: str
    category: str
    dimensions: dict
    volume_capacity: float
    weight_capacity: float
    depot_id: int
