from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
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

    def __repr__(self):
        return f"<Address(lat={self.latitude}, lon={self.longitude}, string_address={self.string_address})>"


Base.metadata.create_all(engine)

