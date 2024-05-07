from source.database.db_init import Order, OrderProduct, Product, Vehicle, Address, Segment, SegmentStatistics
from source.database.db_queries import get_objects
from source.Client1C.http_client_1c import HTTPClient1C
from math import cos, pi
from ortools_vrp_solver import create_data_model, solve


class VRPWrapper:

    zones_to_addresses: dict
    zones_to_vehicles: dict
    address_to_order_contents: dict
    orders: list
    vehicles: list

    def __init__(self, url):
        self.url = url
        self.client1c = HTTPClient1C(url)

    def run(self):
        self._load_orders()
        self._load_vehicles()
        self._assign_vehicles_to_zones()
        self._solve_vrp_for_each_zone()

    def _solve_vrp_for_each_zone(self):
        """
        Solves the VRP for each zone using ortools and returns the solutions.
        :return: list of solutions
        """
        solutions = []
        for zone_id, (vehicle_ids, vehicle_capacities) in self.zones_to_vehicles.items():
            zone_content = self.get_zone_content(zone_id)
            zone_nodes = list(zone_content.keys())

            zone_demands = self._get_zone_demands(zone_content)

            distances, durations = self._calc_distances_durations(zone_nodes)

            data = create_data_model(zone_demands, distances, durations, vehicle_capacities)
            solution = solve(data)

            if solution is not None:
                converted_solution = self._convert_solution_data(solution)
                solutions.append(solution)

        return solutions

    def _convert_solution_data(self, solution):
        # TODO
        return solution

    @staticmethod
    def _get_zone_demands(zone_content):
        zone_demands = []
        for address_id, address_content in zone_content.items():
            address_demands = sum([
                address_content[product_id]["quantity"]
                for product_id in range(len(address_content))
            ])
            zone_demands.append(address_demands)
        return zone_demands

    @staticmethod
    def _calc_distances_durations(nodes) -> tuple[dict, dict]:
        """
        Calculates 'matrices' of distances and durations between all nodes in the zone.
        :param nodes: list of ids of nodes
        :return: tuple of dict for distances and dict for durations between all nodes in the zone
        """

        distances = dict()
        durations = dict()

        # Double loop through all nodes
        for from_node in nodes:
            for to_node in nodes:

                # Distance and duration between the same node is 0
                if from_node == to_node:
                    distances[(from_node, to_node)] = 0
                    durations[(from_node, to_node)] = 0

                # Distance and duration between nodes in different zones is calculated using the average of known data
                else:
                    # Get segment statistics for the segment between the two nodes
                    segment = get_objects(class_name=Segment, address_1_id=from_node, address_2_id=to_node)[0]
                    segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])

                    # Calculate average distance and duration between the two nodes
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
        return distances, durations

    def _load_orders(self):
        self.address_to_order_contents = dict()
        self.zones_to_addresses = dict()

        # Load available orders from the database
        self.orders = get_objects(class_name=Order, status=0)

        # Loop through each order
        for order in self.orders:
            address_id = order["address_id"]
            order_products = get_objects(class_name=OrderProduct, order_id=order["id"])
            order_content = []

            # Loop through products for this order
            for order_product in order_products:
                # Get product details
                product = get_objects(class_name=Product, product_id=order_product["product_id"])[0]

                # Format product dimensions
                product_dims = self.tire_dims_to_external_mm(product["dimensions"])

                # Add product to order contents
                order_content.append({
                    "product_id": product["id"],
                    "dimensions": product_dims,
                    "quantity": order_product["quantity"]
                })

            # Get id of delivery zone the address belongs
            zone_id = get_objects(class_name=Address, address_id=address_id)[0]["delivery_zone_id"]
            if zone_id not in self.zones_to_addresses:
                self.zones_to_addresses[zone_id] = [address_id]
            else:
                self.zones_to_addresses[zone_id].append(address_id)
            self.address_to_order_contents[address_id] = order_content

    def _load_vehicles(self):
        # Load available vehicles from 1C
        available_vehicles = self.client1c.get_available_vehicles()

        self.vehicles = []
        for av_vehicle in available_vehicles["vehicles"]:
            vehicle = get_objects(class_name=Vehicle, name=av_vehicle["name"])[0]
            self.vehicles.append(vehicle)

    @staticmethod
    def tire_dims_to_external_mm(tire_dims: list):
        """converts standard tire dimensions to dimensions of a cylinder bounding a tire"""
        width = tire_dims[0]
        height = tire_dims[1]
        diameter = tire_dims[2]

        diameter_mm = diameter * 25.4 + width * height / 100

        return [diameter_mm, width]

    @staticmethod
    def calc_rough_vehicle_capacity(tire_dims: list, vehicle_dims: list):
        t_diameter = tire_dims[0]
        t_height = tire_dims[1]

        # Get vehicle dimensions
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

    def pack_tires_to_vehicles(self, tire_count: int, tire_dims: list, vehicles: list):
        """packs tires into vehicles"""
        tires_packed = 0

        assigned_vehicles_ids = []
        assigned_vehicles_capacities = []

        for vehicle in vehicles:
            # Check if all tires have been packed
            if tires_packed >= tire_count:
                break

            # Calculate total rough capacity
            rough_capacity = self.calc_rough_vehicle_capacity(tire_dims, vehicle["dimensions"])

            # Assign next vehicle
            assigned_vehicles_ids.append(vehicle["id"])
            assigned_vehicles_capacities.append(rough_capacity)

            if rough_capacity >= tire_count - tires_packed:
                break
            tires_packed += rough_capacity

        if tires_packed < tire_count:
            raise Warning("Not enough vehicles to pack tires for the last zone")

        return assigned_vehicles_ids, assigned_vehicles_capacities

    @staticmethod
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

    def get_zone_content(self, zone_id):
        # Get orders contents for addresses in the current zone
        zone_content = {
            address_id: self.address_to_order_contents[address_id]
            for address_id in self.zones_to_addresses[zone_id]
        }
        return zone_content

    def _assign_vehicles_to_zones(self):
        """assigns vehicles to zones"""

        # TODO: sort zones by average address distance from hub (far zones must be handled first)

        self.zones_to_vehicles = dict()

        # Get ids of available vehicles
        available_vehicles_ids = [vehicle["id"] for vehicle in self.vehicles]

        # Loop through each zone and roughly pack tires to vehicles
        for zone_id, addresses in self.zones_to_addresses.items():
            #  Get orders contents for addresses in the current zone
            zone_addresses_contents = self.get_zone_content(zone_id)

            # Get the biggest tire dimensions and total tires count in the current zone
            dims, count = self.get_biggest_tire_and_total_tires_count(zone_addresses_contents)

            # TODO: add some manipulations with zones to send vehicles of appropriate class

            assigned_vehicles_ids, assigned_vehicles_capacities = self.pack_tires_to_vehicles(count, dims, self.vehicles)
            self.zones_to_vehicles[zone_id] = assigned_vehicles_ids, assigned_vehicles_capacities

            for vehicle_id in assigned_vehicles_ids:
                if vehicle_id in available_vehicles_ids:
                    available_vehicles_ids.remove(vehicle_id)

            if len(available_vehicles_ids) == 0:
                # No more available vehicles
                break

