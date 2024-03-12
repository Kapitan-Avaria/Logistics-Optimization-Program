from sqlalchemy import create_engine, Column, Integer, Float, String, DECIMAL, Text, JSON, Date, Time, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import database_exists, create_database


engine = create_engine("sqlite+pysqlite:///../database.db")

if not database_exists(engine.url):
    create_database(engine.url)
print(database_exists(engine.url))


Base = declarative_base()


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    string_address = Column(String, unique=True)
    machine_address = Column(String, unique=True)
    delivery_zone_id = Column(Integer, ForeignKey("delivery_zones.id"))
    comment = Column(Text)

    __table_args__ = (UniqueConstraint('latitude', 'longitude', name='_address_coords_uc'),)

    def __repr__(self):
        return f"<Address(lat={self.latitude}, lon={self.longitude}, string_address={self.string_address})>"


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    address_1_id = Column(Integer, ForeignKey("addresses.id"))
    address_2_id = Column(Integer, ForeignKey("addresses.id"))
    length = Column(Float)

    __table_args__ = (UniqueConstraint('address_1_id', 'address_2_id', name='_segment_uc'),)


class SegmentStatistics(Base):
    __tablename__ = "segment_statistics"

    segment_id = Column(Integer, ForeignKey("segments.id"), primary_key=True)
    record_id = Column(Integer, primary_key=True)
    route_duration = Column(Integer)
    date = Column(Date)
    start_time = Column(Time)
    week_day = Column(Integer)
    json_response = Column(JSON)


class DeliveryZone(Base):
    __tablename__ = "delivery_zones"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    number = Column(String)
    client_id = Column(Integer, ForeignKey("clients.id"))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    datetime = Column(DateTime)
    delivery_time_start = Column(Time)
    delivery_time_end = Column(Time)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    route_data = Column(JSON)   # Упорядоченный список адресов доставки и время прохождения промежутков
    date = Column(Date)
    time_start = Column(Time)
    time_end = Column(Time)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String)
    dimensions = Column(JSON)   # inner: depth, width, height; outer_dimensions: ...
    weight_capacity = Column(Integer)


class VehicleGeodata(Base):
    __tablename__ = "vehicles_geodata"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    datetime = Column(DateTime)
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    form_factor = Column(Integer, ForeignKey("form_factors.id"))
    dimensions = Column(JSON)   # spatial dimensions in the format corresponding to the form_factor


class OrderProduct(Base):
    __tablename__ = "orders_products"

    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer)


class FormFactor(Base):
    __tablename__ = "form_factors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    dimensions_template = Column(JSON)


Base.metadata.create_all(engine)
