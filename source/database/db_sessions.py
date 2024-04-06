from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from source.database.db_init import engine, Address, Order, DeliveryZone, Client, Product, OrderProduct, Vehicle, FormFactor, \
    VehicleGeodata, Segment, SegmentStatistics
from decimal import Decimal
import numpy as np


def use_with_session(func):
    """Decorator function that wraps the func with 'with Session() ... session.commit()',
    if 'session' argument is not provided"""

    def wrapper(*args, **kwargs):
        # If existing session provided, continues with default function behaviour
        if "session" in kwargs.keys() or (True in map(lambda x: isinstance(x, Session), args) if len(args) > 0 else False):
            return func(*args, **kwargs)

        # If the session is not provided, creates new one
        with Session(bind=engine) as session:
            ret = func(*args, **kwargs, session=session)
            session.commit()
        return ret

    return wrapper


@use_with_session
def insert_orders(orders: list[dict], session: Session):
    for order in orders:
        existing_order: Order = select_existing_object(session, Order, number=order["number"])

        existing_order.date = order["datetime"]

        client: Client = select_existing_object(session, Client, name=order["client"])
        existing_order.client_id = client.id

        address: Address = select_existing_object(session, Address, string_address=order["address"])
        if address.comment is None and order["address_comment"]:
            address.comment = order["address_comment"]
        if address.latitude is None and address.longitude is None and order["geo_location"]:
            address.latitude = Decimal(order["geo_location"]["latitude"])
            address.longitude = Decimal(order["geo_location"]["longitude"])
        if address.delivery_zone_id is None and order["delivery-zone"]:
            delivery_zone: DeliveryZone = select_existing_object(session, DeliveryZone, name=order["delivery-zone"])
            address.delivery_zone_id = delivery_zone.id
        existing_order.address_id = address.id

        existing_order.delivery_time_start = order["delivery-time-start"]
        existing_order.delivery_time_end = order["delivery-time-end"]

        existing_order.status = 0

        if "products" in order.keys():
            for prd in order["products"]:
                product: Product = select_existing_object(session, Product, name=prd["name"])
                product_in_order: OrderProduct = select_existing_object(
                    session,
                    OrderProduct,
                    order_id=existing_order.id,
                    product_id=product.id
                )
                product_in_order.quantity = prd["quantity"]


@use_with_session
def get_orders(session: Session, **kwargs):
    orders = select_many_objects(session, Order, **kwargs)
    res = [extract_object_as_dict(order) for order in orders]
    return res


@use_with_session
def insert_addresses(addresses: list, session: Session):
    for address_string in addresses:
        select_existing_object(session, Address, string_address=address_string)


@use_with_session
def insert_segments_where_lacking(required_segments_number, session: Session):
    addresses = session.query(Address).all()
    for address in addresses:
        segments = session.query(Segment).filter_by(address_1_id=address.id).all()
        segments_number = len(segments)
        # If there are enough outgoing segments, skip the address
        if segments_number >= required_segments_number:
            continue

        # Calc direct distances from this address to another
        direct_distances = calc_direct_distances(
            np.array(float(address.latitude)),
            np.array(float(address.longitude)),
            np.array([float(address_2.latitude) for address_2 in addresses]),
            np.array([float(address_2.longitude) for address_2 in addresses])
        )
        sorted_indices = direct_distances.argsort()

        for i in sorted_indices:
            if address.id == addresses[i].id:
                continue

            segment_exists = bool(
                session.query(Segment).filter_by(
                    address_1_id=address.id,
                    address_2_id=addresses[i].id
                ).all()
            )

            if segment_exists:
                continue

            select_existing_object(
                session,
                Segment,
                address_1_id=address.id,
                address_2_id=addresses[i].id,
                direct_distance=direct_distances[i]
            )
            segments_number += 1

            if segments_number >= required_segments_number:
                break


def calc_direct_distances(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    # lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 * 1000  # Radius of earth in meters.
    return c * r


@use_with_session
def insert_vehicles(vehicles: list[dict], session: Session):
    for vehicle in vehicles:
        existing_vehicle: Vehicle = select_existing_object(session, Vehicle, name=vehicle["name"])
        existing_vehicle.category = vehicle["category"]
        existing_vehicle.dimensions = {"inner": vehicle["dimensions"]}
        existing_vehicle.weight_capacity = vehicle["weight-capacity"]


@use_with_session
def insert_products(products: list[dict], session: Session):
    for product in products:
        existing_product: Product = select_existing_object(session, Product, name=product["name"])
        form_factor: FormFactor = select_existing_object(session, FormFactor, name=product["form-factor"])
        existing_product.form_factor = form_factor.id
        existing_product.dimensions = product["dimensions"]


@use_with_session
def insert_vehicle_geodata(data, session: Session):
    for vehicle_data in data:
        existing_vehicle: Vehicle = select_existing_object(session, Vehicle, name=vehicle_data["vehicle"])
        for record in vehicle_data["geodata"]:
            new_data = VehicleGeodata(
                vehicle_id=existing_vehicle.id,
                datetime=record["datetime"],
                latitude=Decimal(record["latitude"]),
                longitude=Decimal(record["longitude"])
            )
            session.add(new_data)


@use_with_session
def insert_segments(segments, session: Session):
    for segment in segments:
        existing_segment: Segment = select_existing_object(
            session,
            Segment,
            address_1_id=segment[0],
            address_2_id=segment[1]
        )


@use_with_session
def get_all_segments(session: Session):
    segments = select_many_objects(session, Segment)
    res = [extract_object_as_dict(s) for s in segments]
    return res


@use_with_session
def insert_segment_statistics(segment_id, route_distance, route_duration, date, start_time, week_day, json_response, session: Session):
    select_existing_object(
        session,
        SegmentStatistics,
        segment_id=segment_id,
        distance=route_distance,
        duration=route_duration,
        date=date,
        start_time=start_time,
        week_day=week_day,
        json_response=json_response     # Добавить в json поле source с вариантами "yandex", "ors", "real"
    )


@use_with_session
def get_coords_from_db_address(session: Session, **kwargs):
    existing_address = select_existing_object(session, Address, **kwargs)

    coords = (float(existing_address.longitude), float(existing_address.latitude)) \
        if (existing_address.longitude is not None and existing_address.latitude is not None) \
        else None

    return coords


@use_with_session
def get_many_coords_from_db_addresses(ids: list, session: Session):
    res = dict()
    for address_id in ids:
        coords = get_coords_from_db_address(session, id=address_id)
        res[address_id] = coords
    return res


@use_with_session
def insert_coords(address_string, coords, session: Session):
    existing_address = select_existing_object(session, Address, string_address=address_string)

    latitude, longitude = coords

    existing_address.latitude = latitude
    existing_address.longitude = longitude


def extract_object_as_dict(obj):
    res: dict = obj.__dict__
    res.pop('_sa_instance_state', None)
    return res


def select_existing_object(session: Session, class_name, **kwargs):
    for key in kwargs.keys():
        if isinstance(kwargs[key], str):
            kwargs[key] = regularize(kwargs[key])

    try:
        q = session.query(class_name).filter_by(**kwargs)
        existing_object = q.one()
    except NoResultFound:
        new_object = class_name(**kwargs)
        session.add(new_object)
        existing_object = new_object
    session.flush()
    return existing_object


def select_many_objects(session: Session, class_name, **kwargs):
    for key in kwargs.keys():
        if isinstance(kwargs[key], str):
            kwargs[key] = regularize(kwargs[key])

    q = session.query(class_name).filter_by(**kwargs)
    objects = q.all()

    return objects


def read_strings_input():
    arr = []

    s = input()

    while s != '':
        arr.append(s)
        s = input()
    return arr


def regularize(s: str):
    # Заменяем нестандартные пробельные символы обычным пробелом
    s = s.replace('\xa0', ' ')

    # Заменяем идущие подряд пробелы одним пробелом
    s = ' '.join(s.split())
    return s
