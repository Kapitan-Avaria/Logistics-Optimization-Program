import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, Float, String, DECIMAL, Text, ForeignKey, UniqueConstraint
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
    delivery_zone = Column(Integer, ForeignKey("delivery_zones.id"))
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
    date = Column(sa.Date)
    start_time = Column(sa.Time)
    week_day = Column(Integer)


Base.metadata.create_all(engine)

