from dataclasses import dataclass


@dataclass
class Problem:
    orders: list
    products: dict
    delivery_zones: dict
    vehicles: list
    clients: list

