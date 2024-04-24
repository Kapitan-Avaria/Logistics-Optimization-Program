from sqlalchemy.orm import Session

from source.database.db_init import Address, Order, DeliveryZone, Client, Product, OrderProduct, Vehicle, FormFactor, \
    VehicleGeodata, Segment, SegmentStatistics
from decimal import Decimal
import numpy as np

from db_utils import use_with_session, select_existing_object, select_many_objects, extract_object_as_dict, calc_direct_distances


@use_with_session
def get_objects(session: Session, **kwargs):
    objects = select_many_objects(session, kwargs['class_name'], **kwargs)
    res = [extract_object_as_dict(obj) for obj in objects]
    return res


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

    longitude, latitude = coords

    existing_address.latitude = latitude
    existing_address.longitude = longitude
