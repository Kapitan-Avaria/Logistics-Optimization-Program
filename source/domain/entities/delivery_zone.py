from dataclasses import dataclass


@dataclass
class DeliveryZone:
    id: int
    name: str
    type: int
    depot_id: int
