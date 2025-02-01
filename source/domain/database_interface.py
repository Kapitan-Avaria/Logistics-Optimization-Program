from abc import ABC, abstractmethod

from source.domain.entities.address import Address
from source.domain.entities.client import Client
from source.domain.entities.delivery_zone import DeliveryZone
from source.domain.entities.order import Order
from source.domain.entities.order_product import OrderProduct
from source.domain.entities.product import Product
from source.domain.entities.route import Route
from source.domain.entities.segment import Segment
from source.domain.entities.segment_statistics import SegmentStatistics
from source.domain.entities.vehicle import Vehicle


class DatabaseInterface(ABC):
    @abstractmethod
    def create_tables(self):
        pass

    @abstractmethod
    def insert_address(self, address: Address):
        pass

    @abstractmethod
    def insert_client(self, client: Client):
        pass

    @abstractmethod
    def insert_delivery_zone(self, delivery_zone: DeliveryZone):
        pass

    @abstractmethod
    def insert_order(self, order: Order):
        pass

    @abstractmethod
    def insert_order_product(self, order_product: OrderProduct):
        pass

    @abstractmethod
    def insert_product(self, product: Product):
        pass

    @abstractmethod
    def insert_route(self, route: Route):
        pass

    @abstractmethod
    def insert_segment(self, segment: Segment):
        pass

    @abstractmethod
    def insert_segment_statistics(self, segment_statistics: SegmentStatistics):
        pass

    @abstractmethod
    def insert_vehicle(self, vehicle: Vehicle):
        pass

    @abstractmethod
    def get_address(self, address_id: int) -> Address:
        pass

    @abstractmethod
    def get_client(self, client_id: int) -> Client:
        pass

    @abstractmethod
    def get_delivery_zone(self, delivery_zone_id: int) -> DeliveryZone:
        pass

    @abstractmethod
    def get_order(self, order_id: int) -> Order:
        pass

    @abstractmethod
    def get_order_product(self, order_id: int, product_id: int) -> OrderProduct:
        pass

    @abstractmethod
    def get_product(self, product_id: int) -> Product:
        pass

    @abstractmethod
    def get_route(self, route_id: int) -> Route:
        pass

    @abstractmethod
    def get_segment(self, segment_id: int) -> Segment:
        pass

    @abstractmethod
    def get_segment_statistics(self, segment_id: int) -> list[SegmentStatistics]:
        pass

    @abstractmethod
    def get_vehicle(self, vehicle_id: int) -> Vehicle:
        pass
