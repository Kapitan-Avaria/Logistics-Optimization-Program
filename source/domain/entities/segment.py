from dataclasses import dataclass


@dataclass
class Segment:
    id: int
    address_1_id: int
    address_2_id: int
    direct_distance: float
