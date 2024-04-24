from source.database.db_init import Order, OrderProduct, Product, Vehicle, Address
from source.database.db_sessions import get_objects
from source.Client1C.HTTPClient1C import HTTPClient1C
from math import cos, pi


def load_orders():
    address_to_order_contents = dict()
    zones_to_addresses = dict()

    # Load available orders from the database
    orders = get_objects(class_name=Order, status=0)

    # Loop through each order
    for order in orders:
        address_id = order["address_id"]
        order_products = get_objects(class_name=OrderProduct, order_id=order["id"])
        order_content = []

        # Loop through products for this order
        for order_product in order_products:
            # Get product details
            product = get_objects(class_name=Product, product_id=order_product["product_id"])[0]

            # Format product dimensions
            product_dims = tire_dims_to_external_mm(product["dimensions"])

            # Add product to order contents
            order_content.append({
                "product_id": product["id"],
                "dimensions": product_dims,
                "quantity": order_product["quantity"]
            })

        # Get id of delivery zone the address belongs
        address_zone_id = get_objects(class_name=Address, address_id=address_id)[0]["delivery_zone_id"]
        if address_zone_id not in zones_to_addresses:
            zones_to_addresses[address_zone_id] = [address_id]
        else:
            zones_to_addresses[address_zone_id].append(address_id)
        address_to_order_contents[address_id] = order_content

    return address_to_order_contents, orders, zones_to_addresses


def load_vehicles():
    # Load available vehicles from 1C
    client1c = HTTPClient1C()
    available_vehicles = client1c.get_available_vehicles()

    vehicles = []
    for av_vehicle in available_vehicles["vehicles"]:
        vehicle = get_objects(class_name=Vehicle, name=av_vehicle["name"])[0]
        vehicles.append(vehicle)
    return vehicles


def tire_dims_to_external_mm(tire_dims: list):
    """converts standard tire dimensions to dimensions of a cylinder bounding a tire"""
    width = tire_dims[0]
    height = tire_dims[1]
    diameter = tire_dims[2]

    diameter_mm = diameter * 25.4 + width * height / 100

    return [diameter_mm, width]


def pack_tires(tire_count: int, tire_dims: list, vehicles: list):
    """packs tires into vehicles"""
    t_diameter = tire_dims[0]
    t_height = tire_dims[1]

    tires_packed = 0

    assigned_vehicles = []
    for vehicle in vehicles:
        # Check if all tires have been packed
        if tires_packed >= tire_count:
            break
        # Assign next vehicle
        assigned_vehicles.append(vehicle)

        # Get vehicle dimensions
        vehicle_dims = vehicle["dimensions"]
        v_depth = vehicle_dims[0]
        v_width = vehicle_dims[1]
        v_height = vehicle_dims[2]

        # Calculate rough capacity
        rough_row_capacity = v_width // t_diameter
        rough_depth_capacity = v_depth // t_diameter
        rough_col_capacity = v_height // t_height

        row_leftover = v_width % t_diameter
        depth_leftover = v_depth % t_diameter

        # Calculate depth capacity if tires can be packed tightly
        if row_leftover >= t_diameter / 2:
            t_diameter_offset = t_diameter * cos(pi / 6)
            rough_depth_capacity = (v_depth - t_diameter) // t_diameter_offset + 1

        # Calculate total rough capacity
        rough_capacity = rough_row_capacity * rough_depth_capacity * rough_col_capacity

        if rough_capacity >= tire_count - tires_packed:
            break
        tires_packed += rough_capacity

    return assigned_vehicles


def get_biggest_tire_and_total_tires_count(address_to_order_contents: dict):
    """returns the biggest tire dimensions in the dict, and the total number of tires"""
    biggest_tire = None
    total_tires_count = 0
    for order_content in address_to_order_contents.values():
        for tire in order_content:
            if biggest_tire is None:
                biggest_tire = tire
            elif tire["dimensions"][0] > biggest_tire["dimensions"][0]:
                biggest_tire = tire

            total_tires_count += tire["quantity"]

    return biggest_tire["dimensions"], total_tires_count


def run():
    address_to_order_contents, orders, zones_to_addresses = load_orders()
    vehicles = load_vehicles()

    for zone_id, addresses in zones_to_addresses.items():
        dims, count = get_biggest_tire_and_total_tires_count(address_to_order_contents)



