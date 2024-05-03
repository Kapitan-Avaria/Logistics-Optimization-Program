from source.database.db_init import Order, OrderProduct, Product, Vehicle, Address, Segment, SegmentStatistics
from source.database.db_queries import get_objects
from source.Client1C.http_client_1c import HTTPClient1C
from math import cos, pi
from ortools_vrp_solver import create_data_model, solve


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


def load_vehicles(url):
    # Load available vehicles from 1C
    client1c = HTTPClient1C(url)
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


def calc_rough_vehicle_capacity(tire_dims: list, vehicle):
    t_diameter = tire_dims[0]
    t_height = tire_dims[1]

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
    return rough_capacity


def pack_tires_to_vehicles(tire_count: int, tire_dims: list, vehicles: list):
    """packs tires into vehicles"""
    tires_packed = 0

    assigned_vehicles_ids = []
    assigned_vehicles_capacities = []

    for vehicle in vehicles:
        # Check if all tires have been packed
        if tires_packed >= tire_count:
            break

        # Calculate total rough capacity
        rough_capacity = calc_rough_vehicle_capacity(tire_dims, vehicle)

        # Assign next vehicle
        assigned_vehicles_ids.append(vehicle["id"])
        assigned_vehicles_capacities.append(rough_capacity)

        if rough_capacity >= tire_count - tires_packed:
            break
        tires_packed += rough_capacity

    if tires_packed < tire_count:
        raise Warning("Not enough vehicles to pack tires for the last zone")

    return assigned_vehicles_ids, assigned_vehicles_capacities


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


def get_zone_content(zone_id, zones_to_addresses, address_to_order_contents):
    # Get orders contents for addresses in the current zone
    zone_addresses_contents = {address_id: address_to_order_contents[address_id] for address_id in zones_to_addresses[zone_id]}
    return zone_addresses_contents


def assign_vehicles_to_zones(vehicles, zones_to_addresses, address_to_order_contents):
    """assigns vehicles to zones"""

    # TO DO: sort zones by average address distance from hub (far zones must be handled first)

    zones_to_vehicles = dict()

    # Get ids of available vehicles
    available_vehicles_ids = [vehicle["id"] for vehicle in vehicles]

    # Loop through each zone and roughly pack tires to vehicles
    for zone_id, addresses in zones_to_addresses.items():
        #  Get orders contents for addresses in the current zone
        zone_addresses_contents = get_zone_content(zone_id, zones_to_addresses, address_to_order_contents)

        # Get the biggest tire dimensions and total tires count in the current zone
        dims, count = get_biggest_tire_and_total_tires_count(zone_addresses_contents)

        # TO DO: add some manipulations with zones to send vehicles of appropriate class

        assigned_vehicles_ids, assigned_vehicles_capacities = pack_tires_to_vehicles(count, dims, vehicles)
        zones_to_vehicles[zone_id] = assigned_vehicles_ids, assigned_vehicles_capacities

        for vehicle_id in assigned_vehicles_ids:
            if vehicle_id in available_vehicles_ids:
                available_vehicles_ids.remove(vehicle_id)

        if len(available_vehicles_ids) == 0:
            # No more available vehicles
            break

    return zones_to_vehicles


def run(url):
    # Load orders and vehicles from the database
    address_to_order_contents, orders, zones_to_addresses = load_orders()
    vehicles = load_vehicles(url)
    zones_to_vehicles = assign_vehicles_to_zones(vehicles, zones_to_addresses, address_to_order_contents)

    for zone_id, (vehicle_ids, vehicle_capacities) in zones_to_vehicles.items():
        zone_content = get_zone_content(zone_id, zones_to_addresses, address_to_order_contents)
        zone_nodes = [address_id for address_id in zone_content.keys()]
        zone_demands = []

        for address_id in zone_nodes:
            address_demands = sum([zone_content[address_id][p]["quantity"] for p in range(len(zone_content[address_id]))])
            zone_demands.append(address_demands)

        distances = dict()
        durations = dict()
        for from_node in zone_nodes:
            for to_node in zone_nodes:
                if from_node == to_node:
                    distances[(from_node, to_node)] = 0
                    durations[(from_node, to_node)] = 0
                else:
                    segment = get_objects(class_name=Segment, address_1_id=from_node, address_2_id=to_node)[0]
                    segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])

                    num_records = len(segment_statistics)
                    sum_dist = 0
                    sum_time = 0

                    for record in range(num_records):
                        sum_dist += segment_statistics[record]["distance"]
                        sum_time += segment_statistics[record]["duration"]
                    avg_dist = sum_dist / num_records
                    avg_time = sum_time / num_records

                    distances[(from_node, to_node)] = avg_dist
                    durations[(from_node, to_node)] = avg_time

        data = create_data_model(zone_demands, distances, durations, vehicle_capacities)
        solve(data)

