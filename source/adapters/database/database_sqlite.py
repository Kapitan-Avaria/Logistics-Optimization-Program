from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, Text, Float, Date, Time, JSON, ForeignKey, UniqueConstraint
)

from source.domain.database_interface import DatabaseInterface

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


metadata = MetaData()


addresses = Table(
    'addresses',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('string_address', Text, unique=True),
    Column('machine_address', Text, unique=True),
    Column('delivery_zone_id', Integer, ForeignKey("delivery_zones.id")),
    UniqueConstraint('latitude', 'longitude', name='_address_coords_uc')
)

segments = Table(
    'segments',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('address_1_id', Integer, ForeignKey("addresses.id")),
    Column('address_2_id', Integer, ForeignKey("addresses.id")),
    Column('direct_distance', Float),
    UniqueConstraint('address_1_id', 'address_2_id', name='_segment_uc')
)

segment_statistics = Table(
    'segment_statistics',
    metadata,
    Column('record_id', Integer, primary_key=True),
    Column('segment_id', Integer, ForeignKey("segments.id")),
    Column('distance', Integer),
    Column('duration', Integer),
    Column('date', Date),
    Column('start_time', Time),
    Column('week_day', Integer),
    Column('json_response', JSON)
)

delivery_zones = Table(
    'delivery_zones',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Text, unique=True),
    Column('type', Integer),
    Column('depot_id', Integer, ForeignKey("addresses.id"))
)

orders = Table(
    'orders',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('number', Text),
    Column('client_id', Integer, ForeignKey("clients.id")),
    Column('address_id', Integer, ForeignKey("addresses.id")),
    Column('date', Date),
    Column('delivery_time_start', Time),
    Column('delivery_time_end', Time),
    Column('comment', Text),
    Column('status', Integer)
)

clients = Table(
    'clients',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Text, unique=True)
)

routes = Table(
    'routes',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Text, unique=True),
    Column('vehicle_id', Integer, ForeignKey("vehicles.id")),
    Column('route_data', JSON),
    Column('date', Date),
    Column('time_start', Time),
    Column('duration', Integer)
)

vehicles = Table(
    'vehicles',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Text, unique=True),
    Column('category', Text),
    Column('dimensions', JSON),
    Column('weight_capacity', Integer)
)

products = Table(
    'products',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Text, unique=True),
    Column('form_factor', Integer),
    Column('dimensions', JSON),
    Column('weight', Integer)
)

order_products = Table(
    'order_products',
    metadata,
    Column('order_id', Integer, ForeignKey("orders.id"), primary_key=True),
    Column('product_id', Integer, ForeignKey("products.id"), primary_key=True),
    Column('quantity', Integer)
)


class DatabaseSQLiteAdapter(DatabaseInterface):
    def __init__(self, database_uri):
        engine = create_engine(database_uri)
        self.__connection = engine.connect()

    def insert_address(self, address: Address):
        query = addresses.insert().values(
            latitude=address.latitude,
            longitude=address.longitude,
            string_address=address.string_address,
            machine_address=address.machine_address,
            delivery_zone_id=address.delivery_zone_id
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_client(self, client: Client):
        query = clients.insert().values(
            name=client.name
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_delivery_zone(self, delivery_zone: DeliveryZone):
        query = delivery_zones.insert().values(
            name=delivery_zone.name,
            type=delivery_zone.type,
            depot_id=delivery_zone.depot_id
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_order(self, order: Order):
        query = orders.insert().values(
            number=order.number,
            client_id=order.client_id,
            address_id=order.address_id,
            date=order.date,
            delivery_time_start=order.delivery_time_start,
            delivery_time_end=order.delivery_time_end,
            comment=order.comment,
            status=order.status
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_order_product(self, order_product: OrderProduct):
        query = order_products.insert().values(
            order_id=order_product.order_id,
            product_id=order_product.product_id,
            quantity=order_product.quantity
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_product(self, product: Product):
        query = products.insert().values(
            name=product.name,
            form_factor=product.form_factor,
            dimensions=product.dimensions,
            volume=product.volume
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_route(self, route: Route):
        query = routes.insert().values(
            name=route.name,
            vehicle_id=route.vehicle_id,
            route_data=route.route_data,
            date=route.date,
            time_start=route.time_start,
            duration=route.duration
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_segment(self, segment: Segment):
        query = segments.insert().values(
            address_1_id=segment.address_1_id,
            address_2_id=segment.address_2_id,
            direct_distance=segment.direct_distance
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_segment_statistics(self, segment_statistic: SegmentStatistics):
        query = segment_statistics.insert().values(
            segment_id=segment_statistic.segment_id,
            distance=segment_statistic.distance,
            duration=segment_statistic.duration,
            date=segment_statistic.date,
            start_time=segment_statistic.start_time,
            week_day=segment_statistic.week_day,
            json_response=segment_statistic.json_response
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def insert_vehicle(self, vehicle: Vehicle):
        query = vehicles.insert().values(
            name=vehicle.name,
            category=vehicle.category,
            dimensions=vehicle.dimensions,
            weight_capacity=vehicle.weight_capacity
        )
        self.__connection.execute(query)
        self.__connection.commit()

    def get_address(self, address_id: int):
        query = addresses.select().where(addresses.c.id == address_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return Address(**row)

    def get_client(self, client_id: int):
        query = clients.select().where(clients.c.id == client_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return Client(**row)

    def get_delivery_zone(self, delivery_zone_id: int):
        query = delivery_zones.select().where(delivery_zones.c.id == delivery_zone_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return DeliveryZone(**row)

    def get_order(self, order_id: int):
        query = orders.select().where(orders.c.id == order_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return Order(**row)

    def get_order_product(self, order_id: int, product_id: int):
        query = order_products.select().where(
            order_products.c.order_id == order_id,
            order_products.c.product_id == product_id
        )
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return OrderProduct(**row)

    def get_product(self, product_id: int):
        query = products.select().where(products.c.id == product_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return Product(**row)

    def get_route(self, route_id: int):
        query = routes.select().where(routes.c.id == route_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return Route(**row)

    def get_segment(self, segment_id: int):
        query = segments.select().where(segments.c.id == segment_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return Segment(**row)

    def get_segment_statistics(self, segment_id: int):
        query = segment_statistics.select().where(segment_statistics.c.segment_id == segment_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return SegmentStatistics(**row)

    def get_vehicle(self, vehicle_id: int):
        query = vehicles.select().where(vehicles.c.id == vehicle_id)
        cursor = self.__connection.execute(query)
        row = cursor.fetchone()
        return Vehicle(**row)
