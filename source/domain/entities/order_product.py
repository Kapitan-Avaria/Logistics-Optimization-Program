from dataclasses import dataclass


@dataclass
class OrderProduct:
    order_id: int
    product_id: int
    quantity: int
