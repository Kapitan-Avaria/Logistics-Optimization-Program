from source.vrp.vrp_solver import CVRPTW
from source.client_1c.http_client_1c import HTTPClient1C
from source.database.db_queries import *


class VRPWrapper:

    def __init__(self):
        self.orders = []
        self.products = dict()
        self.vehicles = []
        self.depot_address = dict()
        self.assigned_vehicles = []
        self.assigned_orders = []
        self.approved_routes = []
        self.actual_volume_ratio = 0.8  # A coefficient to diminish volume of the vehicle

    def prepare_data(self):
        num_orders = len(self.orders)

        addresses = [self.depot_address] + [self.orders[o]["address"] for o in range(num_orders)]
        try:
            distance_evaluator = self.create_distance_evaluator([a["id"] for a in addresses])
        except NoSegmentDataError:
            distance_evaluator = None

        locations = [(a["longitude"], a["latitude"]) for a in addresses]

        demands = [{}] + [
            {p["product_id"]: p["quantity"] for p in self.orders[o]["products"]} for o in range(num_orders)
        ]
        product_volumes = {p["product_id"]: p["volume"] for p in self.products}
        time_windows = [(0, 24)] + [self.orders[o] for o in range(num_orders)]
        vehicle_capacities = [v["dimensions"]["inner"]["volume"] * self.actual_volume_ratio for v in self.vehicles]

        cvrptw = CVRPTW(locations, demands, product_volumes, time_windows, vehicle_capacities, distance_evaluator)
        routes = cvrptw.construct_routes()
        cvrptw.print_routes(routes)

    def load_data(self, db_is_empty, url_1c):
        """
        Loads the necessary data from 1C and from the local db
        """
        client = HTTPClient1C(url_1c)

        # Load historical and utility data from 1C if database was created for the first time
        if db_is_empty:
            all_products = client.get_all_products()
            upsert_products(all_products)

            all_vehicles = client.get_all_vehicles()
            upsert_vehicles(all_vehicles)

            archived_orders = client.get_archived_orders()
            upsert_orders(archived_orders)

        # Load operational data from 1C
        # Load available orders to the database
        available_orders = client.get_available_orders()
        upsert_orders(available_orders)

        # Load available vehicles from 1C
        available_vehicles = client.get_available_vehicles()
        for v in available_vehicles:
            vehicle_obj = get_objects(class_name=Vehicle, name=v["name"])
            if len(vehicle_obj) == 0:
                upsert_vehicles(client.get_vehicle(v["name"]))

        # ***************************************
        # Load available orders from the database
        self.orders = get_objects(class_name=Order, status=0)
        self.products = dict()

        for o, order in enumerate(self.orders):
            # Load products and address in each order
            order_products = get_objects(class_name=OrderProduct, order_id=order["id"])
            address = get_objects(class_name=Address, id=order["address_id"])
            self.orders[o]["products"] = order_products
            self.orders[o]["address"] = address

            # Save all the products that was in all orders
            for p in order_products:
                p_obj = get_objects(class_name=Product, id=p["product_id"])[0]
                self.products[p["product_id"]] = p_obj

        # Load available vehicles
        self.vehicles = []
        for av_vehicle in available_vehicles():
            vehicle = get_objects(class_name=Vehicle, name=av_vehicle["name"])[0]
            self.vehicles.append(vehicle)

        random_zone = get_objects(class_name=DeliveryZone, id=self.orders[0]["address"]["delivery_zone_id"])
        self.depot_address = get_objects(class_name=Address, id=random_zone["depot_id"])[0]

    @staticmethod
    def create_distance_evaluator(addresses_ids):
        """
        Calculates 'matrices' of distances and durations between all nodes in the zone.
        :param addresses_ids: list of ids of addresses
        :return: evaluator function
        """
        distances = []

        # Double loop through all nodes
        for i, from_node in enumerate(addresses_ids):
            distances.append([])
            for j, to_node in enumerate(addresses_ids):

                # Distance between the same node is 0
                if from_node == to_node:
                    distances[i].append(0)

                # Distance and duration between nodes in different zones is calculated using the average of known data
                else:
                    # Get segment statistics for the segment between the two nodes
                    segment = get_objects(class_name=Segment, address_1_id=from_node, address_2_id=to_node)[0]
                    segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])

                    # Calculate average distance and duration between the two nodes
                    num_records = len(segment_statistics)

                    if num_records == 0:
                        raise NoSegmentDataError(f'There is no data records for segment {segment["id"]} with nodes ({from_node} -> {to_node})')

                    sum_dist = 0
                    sum_time = 0
                    for record in range(num_records):
                        sum_dist += segment_statistics[record]["distance"]
                        sum_time += segment_statistics[record]["duration"]
                    avg_dist = sum_dist / num_records
                    distances[i].append(avg_dist)

        def distance_evaluator(from_node, to_node):
            nonlocal distances
            return distances[from_node][to_node]

        return distance_evaluator


class NoSegmentDataError(Exception):
    pass
