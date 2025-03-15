from dataclasses import dataclass
from datetime import date, time


@dataclass
class Order:
    id: int
    number: str
    client_id: int
    address_id: int
    date: date
    delivery_time_start: time
    delivery_time_end: time
    comment: str
    status: int
