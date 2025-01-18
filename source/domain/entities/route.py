from dataclasses import dataclass
from datetime import date, time


@dataclass
class Route:
    id: int
    name: str
    vehicle_id: int
    route_data: list
    date: date
    time_start: time
    duration: int
