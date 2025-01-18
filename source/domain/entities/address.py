from dataclasses import dataclass


@dataclass
class Address:
    id: int
    latitude: float
    longitude: float
    string_address: str
    machine_address: str
    delivery_zone_id: int
