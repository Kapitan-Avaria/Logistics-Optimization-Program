from sqlalchemy.orm import Session
from decimal import Decimal
import numpy as np
from datetime import datetime

from source.database.__all_models import *
from source.database.db_utils import use_with_session, select_existing_object, select_many_objects, extract_object_as_dict, calc_direct_distances


@use_with_session
def get_objects(session: Session, **kwargs):
    class_name = kwargs['class_name']
    kwargs.pop("class_name", None)
    objects = select_many_objects(session, class_name, **kwargs)
    res = [extract_object_as_dict(obj) for obj in objects]

    return res


@use_with_session
def upsert_orders(orders: list[dict], session: Session):
    for order in orders:
        existing_order: Order = select_existing_object(session, Order, number=order["number"])

        if existing_order.date is None:
            date = datetime.strptime(order["date"], "%Y-%m-%d")
            existing_order.date = date

        if existing_order.client_id is None:
            client: Client = select_existing_object(session, Client, name=order["client"])
            existing_order.client_id = client.id

        if existing_order.address_id is None:
            address = insert_address_from_order(order, session)
            existing_order.address_id = address.id

        if existing_order.delivery_time_start is None and order["delivery-time-start"]:
            start_time = datetime.strptime(order["delivery-time-start"], "%H:%M").time()
            existing_order.delivery_time_start = start_time
        if existing_order.delivery_time_end is None and order["delivery-time-end"]:
            end_time = datetime.strptime(order["delivery-time-end"], "%H:%M").time()
            existing_order.delivery_time_end = end_time

        if existing_order.comment is None and order["comment"]:
            existing_order.comment = order["comment"]

        if existing_order.status is None and order["status"]:
            existing_order.status = order["status"]

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


def insert_address_from_dict(d: dict, session: Session):
    address = select_existing_object(session, Address, string_address=d["string_address"])
    if address.latitude is None or address.longitude is None:
        if d["geo-location"]:
            address.longitude = Decimal(d["geo-location"]["longitude"])
            address.latitude = Decimal(d["geo-location"]["latitude"])
    if address.delivery_zone_id is None and d["delivery-zone"]:
        delivery_zone: DeliveryZone = select_existing_object(session, DeliveryZone, name=d["delivery-zone"])
        address.delivery_zone_id = delivery_zone.id
    return address


@use_with_session
def insert_addresses(addresses: list, session: Session):
    for a in addresses:
        insert_address_from_dict(a, session)


@use_with_session
def insert_address_from_order(order, session: Session):
    address = insert_address_from_dict(order, session)
    return address


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

            segment = session.query(Segment).filter_by(address_1_id=address.id, address_2_id=addresses[i].id).all()
            segment_exists = bool(segment)

            if segment_exists:
                if segment[0]["direct_distance"] is not None:
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
def upsert_vehicles(vehicles: list[dict], session: Session):
    for vehicle in vehicles:
        existing_vehicle: Vehicle = select_existing_object(session, Vehicle, name=vehicle["name"])

        if existing_vehicle.category is None and vehicle["category"]:
            existing_vehicle.category = vehicle["category"]

        if existing_vehicle.dimensions is None and vehicle["dimensions"]:
            volume = vehicle["dimensions"][0] * vehicle["dimensions"][1] * vehicle["dimensions"][2]
            existing_vehicle.dimensions = {"inner": vehicle["dimensions"], "volume": volume}

        if existing_vehicle.weight_capacity is None and vehicle["weight-capacity"]:
            existing_vehicle.weight_capacity = vehicle["weight-capacity"]


@use_with_session
def upsert_products(products: list[dict], session: Session):
    def tire_dims_to_external_mm(tire_dims: list):
        """converts standard tire dimensions to dimensions of the box bounding the tire"""
        width = tire_dims[0]
        height = tire_dims[1]
        diameter = tire_dims[2]

        diameter_m = (diameter * 25.4 + 2 * width * (height / 100)) / 1000
        width_m = width / 1000

        return [diameter_m, diameter_m, width_m]

    for product in products:
        existing_product: Product = select_existing_object(session, Product, name=product["name"])

        if existing_product.form_factor is None:
            form_factor: FormFactor = select_existing_object(session, FormFactor, name=product["form-factor"])
            existing_product.form_factor = form_factor.id
        if existing_product.dimensions is None and product["dimensions"]:
            existing_product.dimensions = product["dimensions"]
        if product["form-factor"] == 'tire':
            dims = tire_dims_to_external_mm(product["dimensions"])
            volume = dims[0] * dims[1] * dims[2]
            existing_product.volume = volume


@use_with_session
def insert_vehicle_geodata(data, session: Session):
    for vehicle_data in data:
        existing_vehicle: Vehicle = select_existing_object(session, Vehicle, name=vehicle_data["vehicle"])
        for record in vehicle_data["geodata"]:
            existing_geodata: VehicleGeodata = select_existing_object(
                session,
                VehicleGeodata,
                vehicle_id=existing_vehicle.id,
                datetime=record["datetime"],
                latitude=Decimal(record["latitude"]),
                longitude=Decimal(record["longitude"])
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
        json_response=json_response
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
