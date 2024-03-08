from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from database.db_init import engine, Address, Order, DeliveryZone, Client, Product, OrderProduct
from decimal import Decimal


def insert_orders(orders: list[dict]):
    with Session(bind=engine) as session:
        for order in orders:
            existing_order = select_existing_object(session, Order, number=order["number"])

            existing_order.date = order["datetime"]

            client = select_existing_object(session, Client, name=order["client"])
            existing_order.client_id = client.id

            address = select_existing_object(session, Address, string_address=order["address"])
            if address.comment is None and order["address_comment"]:
                address.comment = order["address_comment"]
            if address.latitude is None and address.longitude is None and order["geo_location"]:
                address.latitude = Decimal(order["geo_location"]["latitude"])
                address.longitude = Decimal(order["geo_location"]["longitude"])
            if address.delivery_zone_id is None and order["delivery-zone"]:
                delivery_zone = select_existing_object(session, DeliveryZone, name=order["delivery-zone"])
                address.delivery_zone_id = delivery_zone.id
            existing_order.address_id = address.id

            existing_order.delivery_time_start = order["delivery-time-start"]
            existing_order.delivery_time_end = order["delivery-time-end"]

            if "products" in order.keys():
                for prd in order["products"]:
                    product = select_existing_object(session, Product, name=prd["name"])
                    product_in_order = select_existing_object(
                        session,
                        OrderProduct,
                        order_id=existing_order.id,
                        product_id=product.id
                    )
                    product_in_order.quantity = prd["quantity"]

        session.commit()


def insert_addresses(addresses):
    with Session(bind=engine) as session:

        for address_string in addresses:
            select_existing_object(session, Address, string_address=address_string)

        session.commit()


def get_coords(address_string):

    with Session(bind=engine) as session:
        existing_address = select_existing_object(session, Address, string_address=address_string)
        
        coords = (existing_address.latitude, existing_address.longitude) \
            if (existing_address.latitude is not None and existing_address.latitude is not None) \
            else None

        session.commit()

    return coords


def insert_coords(address_string, coords):
    with Session(bind=engine) as session:
        existing_address = select_existing_object(session, Address, string_address=address_string)

        latitude, longitude = coords

        existing_address.latitude = latitude
        existing_address.longitude = longitude

        session.commit()


def select_existing_object(session, class_name, **kwargs):
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
    return existing_object


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
