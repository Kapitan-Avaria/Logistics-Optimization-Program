from source.vrp.vrp_solver import CVRPTW
from source.client_1c.http_client_1c import HTTPClient1C
from source.routing.routing_wrapper import RoutingWrapper
from source.geocoding.geocoding_wrapper import GeocodingWrapper
from source.database.db_queries import *
from source.config import Config

from datetime import datetime, date, timedelta
from copy import deepcopy
import folium
import numpy as np


class VRPWrapper:

    def __init__(self):
        self.status_1c = None

        self.orders = []
        self.products = dict()
        self.available_vehicles = []
        self.vehicles = []
        self.depot_address = dict()
        self.clients = dict()
        self.delivery_zones = dict()

        self.unassigned_vehicles = []
        self.unassigned_orders = []
        self.approved_routes = []
        self.actual_volume_ratio = 1.  # A coefficient to diminish volume of the vehicle
        self.request_coords_on_load = True
        self.map = folium.Map()

        # VRP data
        self.num_orders = 0
        self.addresses: list[dict] = []
        self.locations = []
        self.demands = []
        self.product_volumes = dict()
        self.time_windows = []
        self.vehicle_capacities = []
        self.vehicle_time_windows = []

    def run(self, vehicles_ids, orders_ids, category_matters=True):
        def vehicle_index_from_vehicle_id(v_id):
            for i in range(len(self.vehicles)):
                if self.vehicles[i]["id"] == v_id:
                    return i
            raise Exception(f"Vehicle with id {v_id} not found")

        def order_index_from_order_id(o_id):
            for i in range(len(self.orders)):
                if self.orders[i]["id"] == o_id:
                    return i
            raise Exception(f"Order with id {o_id} not found")

        def convert_routes(routes, locations_indices):
            converted_routes = []
            for route in routes:
                converted_route = []
                if len(route) > 0:
                    for i, point in enumerate(route):
                        converted_route.append({
                            # 'order': self.orders[locations_indices[point[0]]],
                            'address': self.addresses[locations_indices[point[0]]],
                            'arrival_time': point[1],
                            'load': point[2],
                            'wait_time': point[3]
                        })
                converted_routes.append(converted_route)
            return converted_routes

        for i, v in enumerate(self.vehicles):
            self.vehicles[i]["routes"] = []

        if category_matters:
            vehicles_indices_b = []
            vehicles_indices_c = []
            addresses_indices_b = [0]
            addresses_indices_c = [0]

            for v_id in vehicles_ids:
                i = vehicle_index_from_vehicle_id(v_id)
                if self.vehicles[i]["category"] == "B":
                    vehicles_indices_b.append(i)
                elif self.vehicles[i]["category"] == "C":
                    vehicles_indices_c.append(i)

            for o_id in orders_ids:
                i = order_index_from_order_id(o_id)
                # self.unassigned_orders.remove(i)
                if self.addresses[i + 1]["delivery_zone_type"] == "B":
                    addresses_indices_b.append(i + 1)
                elif self.addresses[i + 1]["delivery_zone_type"] == "C":
                    addresses_indices_c.append(i + 1)

            routes_b = self.build_routes(vehicles_indices_b, addresses_indices_b)
            routes_c = self.build_routes(vehicles_indices_c, addresses_indices_c, start_from_farthest=True)

            for i, v in enumerate(vehicles_indices_b):
                self.vehicles[v]["routes"].append(convert_routes([routes_b[i]], addresses_indices_b)[0])
            for i, v in enumerate(vehicles_indices_c):
                self.vehicles[v]["routes"].append(convert_routes([routes_c[i]], addresses_indices_c)[0])
        else:
            vehicles_indices = [vehicle_index_from_vehicle_id(v_id) for v_id in vehicles_ids]
            addresses_indices = [order_index_from_order_id(o_id) + 1 for o_id in orders_ids]
            routes = self.build_routes(vehicles_indices, addresses_indices)
            for v in vehicles_indices:
                self.vehicles[v]["routes"].append(convert_routes([routes[v]], addresses_indices)[0])
        self.draw_map()

    def calc_total_loc_volume(self, loc):
        if loc == 0:
            return 0
        loc_volume = 0
        for product, quantity in self.demands[loc].items():
            loc_volume += quantity * self.product_volumes[product]
        return loc_volume

    def build_routes(self, vehicles_indices, addresses_indices, start_from_farthest=False):
        """
        Solves CVRPTW problem for the selected vehicles and addresses
        """
        try:
            # raise Exception("ORS-based evaluator is too slow right now and not invoked")
            distance_evaluator = self.create_distance_evaluator([self.addresses[i] for i in addresses_indices])
        except Exception as e:
            print(e)
            distance_evaluator = None

        cvrptw = CVRPTW(
            [self.locations[a] for a in addresses_indices],
            [self.demands[a] for a in addresses_indices],
            self.product_volumes,
            [self.time_windows[a] for a in addresses_indices],
            [self.vehicle_capacities[v] for v in vehicles_indices],
            vehicle_time_windows=self.vehicle_time_windows,
            distance_evaluator=distance_evaluator,
            loc_clusters=[self.addresses[a]["delivery_zone_id"] for a in addresses_indices]
        )
        routes = cvrptw.construct_routes(start_from_farthest=start_from_farthest)
        cvrptw.print_routes(routes)
        return routes

    def draw_map(self):
        """
        Draws the map with the routes
        """
        self.map = folium.Map(location=[self.depot_address["latitude"], self.depot_address["longitude"]], zoom_start=8)
        colors = [
            'red', 'blue', 'gray', 'green', 'pink', 'darkgreen', 'darkred', 'orange',
            'darkblue', 'purple', 'cadetblue', 'black'
        ]
        routes = [v["routes"][0] for v in self.vehicles if len(v["routes"]) > 0]
        routes = [route for route in routes if len(route) > 0]
        for i in range(1, len(self.locations)):
            if i-1 in self.unassigned_orders:
                folium.Marker(
                    location=[self.locations[i][1], self.locations[i][0]],
                    tooltip=f"Адрес: {self.addresses[i]['string_address']},\n[{self.orders[i-1]['delivery_time_start']}, {self.orders[i-1]['delivery_time_end']}]",
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(self.map)
        for r, route in enumerate(routes):
            route_group = folium.FeatureGroup(name=f'<span style="color: {colors[r % len(colors)]};">Route {r + 1}</span>')
            for i in range(len(route)):
                loc = route[i]["address"]
                marker = folium.Marker(
                    location=[loc["latitude"], loc["longitude"]],
                    tooltip=f"Location: {i}, "
                            f"Arrival Time: {route[i]['arrival_time']:.2f}, "
                            f"Load: {route[i]['load']:.2f}, "
                            f"Wait Time: {route[i]['wait_time']:.2f}",
                    icon=folium.Icon(color="green", icon="ok-sign")
                )
                route_group.add_child(marker)
            route_locations = [[self.depot_address["latitude"], self.depot_address["longitude"]]] + [
                [route[i]["address"]["latitude"], route[i]["address"]["longitude"]] for i in range(len(route))
            ]
            polyline = folium.PolyLine(
                locations=route_locations,
                color=colors[r % len(colors)],
                weight=2.5,
                opacity=1
            )
            route_group.add_child(polyline)
            self.map.add_child(route_group)
        folium.Marker(
            location=[self.depot_address["latitude"], self.depot_address["longitude"]],
            tooltip=f"Склад: {self.depot_address['string_address']}",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(self.map)

        folium.LayerControl(collapsed=False).add_to(self.map)

    @staticmethod
    def reload_address_if_not_geocoded(address):
        """
        If there is no geolocation for the address, then request it from API and reload address
        """
        if address["longitude"] is None or address["latitude"] is None:
            gw = GeocodingWrapper()
            coords = gw.get_coordinates(address["string_address"])
            insert_coords(address["string_address"], coords)
            address = get_objects(class_name=Address, id=address["id"])[0]
        return address

    def request_data_from_1c(self, db_is_empty, url_1c):
        """
        Loads the necessary data from 1C
        """
        client = HTTPClient1C(url_1c)
        self.status_1c = client.is_available()
        if not self.status_1c:
            return

        # Load historical and utility data from 1C if database was created for the first time
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

        if self.request_coords_on_load:
            # Bulk geocoding the addresses that have no geolocation
            for o, order in enumerate(available_orders):
                address = get_objects(class_name=Address, string_address=order["address"])[0]
                self.reload_address_if_not_geocoded(address)

        # Load available vehicles from 1C
        self.available_vehicles = client.get_available_vehicles()
        for v in self.available_vehicles:
            vehicle_obj = get_objects(class_name=Vehicle, name=v["name"])
            if len(vehicle_obj) == 0:
                upsert_vehicles(client.get_vehicle(v["name"]))

    def load_data_from_db(self):
        """
        Loads the necessary data from 1C and from the local db
        """
        # ***************************************
        # Load available orders from the database
        self.orders = get_objects(class_name=Order, status=0)
        self.products = dict()
        cfg = Config()

        for o, order in enumerate(self.orders):
            # Load products and address in each order
            order_products = get_objects(class_name=OrderProduct, order_id=order["id"])
            address = get_objects(class_name=Address, id=order["address_id"])[0]
            client = get_objects(class_name=Client, id=order["client_id"])[0]
            if self.request_coords_on_load:
                address = self.reload_address_if_not_geocoded(address)

            delivery_zone = get_objects(class_name=DeliveryZone, id=address["delivery_zone_id"])[0]
            self.delivery_zones[address["delivery_zone_id"]] = delivery_zone
            address["delivery_zone"] = delivery_zone["name"]
            address["delivery_zone_type"] = delivery_zone["type"]
            self.clients[client["id"]] = client

            self.orders[o]["products"] = order_products
            self.orders[o]["address"] = address

            # Save all the products that was in all orders
            for p in order_products:
                p_obj = get_objects(class_name=Product, id=p["product_id"])[0]
                self.products[p["product_id"]] = p_obj

        # Load available vehicles from db
        self.vehicles = []
        av_veh = self.available_vehicles if self.available_vehicles else get_objects(class_name=Vehicle)
        for av_vehicle in av_veh:
            vehicle = get_objects(class_name=Vehicle, name=av_vehicle["name"])[0]
            vehicle["routes"] = []
            self.vehicles.append(vehicle)

        try:
            random_zone = get_objects(class_name=DeliveryZone, id=self.orders[0]["address"]["delivery_zone_id"])[0]
        except IndexError:
            print("[WARN]: No orders in the database")
            return

        try:
            self.depot_address = get_objects(class_name=Address, id=random_zone["depot_id"])[0]
        except IndexError:
            print("[WARN]: Depot address was not loaded, inserting default")
            self.depot_address = get_objects(class_name=Address, string_address=cfg.DEPOT_ADDRESS)[0]
        self.depot_address = self.reload_address_if_not_geocoded(self.depot_address)

        self.unassigned_vehicles = [i for i in range(len(self.vehicles))]
        self.unassigned_orders = [i for i in range(len(self.orders))]

        inserted = insert_segments_where_lacking(100000)
        if inserted:
            self.request_statistics_from_api()

        # ***************************
        # Prepare VRP data
        self.actual_volume_ratio = cfg.ACTUAL_VOLUME_RATIO

        self.num_orders = len(self.orders)

        self.addresses = [self.depot_address] + [self.orders[o]["address"] for o in range(self.num_orders)]
        self.locations = [(a["longitude"], a["latitude"]) for a in self.addresses]

        self.demands = [{}] + [
            {p["product_id"]: p["quantity"] for p in self.orders[o]["products"]} for o in range(self.num_orders)
        ]
        self.product_volumes = {k: p["volume"] for k, p in self.products.items()}
        self.time_windows = [(0, 24)] + [
            (
                self.orders[o]["delivery_time_start"].hour + self.orders[o]["delivery_time_start"].minute / 60,
                self.orders[o]["delivery_time_end"].hour + self.orders[o]["delivery_time_end"].minute / 60
            ) for o in range(self.num_orders)
        ]
        self.vehicle_capacities = [v["dimensions"]["volume"] * self.actual_volume_ratio for v in self.vehicles]

        def add_times(t, time_delta_string):
            (h, m) = time_delta_string.split(':')
            d = timedelta(hours=int(h), minutes=int(m))
            t += d
            return t

        # Creating time windows for vehicles
        shift_start_b = datetime.strptime(cfg.DEFAULT_SHIFT_START_B, "%H:%M")
        shift_end_b = add_times(shift_start_b, cfg.DEFAULT_SHIFT_DURATION_B).time()
        shift_start_c = datetime.strptime(cfg.DEFAULT_SHIFT_START_C, "%H:%M")
        shift_end_c = add_times(shift_start_c, cfg.DEFAULT_SHIFT_DURATION_C).time()
        shift_start_b = shift_start_b.time()
        shift_start_c = shift_start_c.time()
        self.vehicle_time_windows = [
            [
                shift_start_b.hour + shift_start_b.minute / 60,
                shift_end_b.hour + shift_end_b.minute / 60
            ] if v["category"] == "B" else [
                shift_start_c.hour + shift_start_c.minute / 60,
                shift_end_c.hour + shift_end_c.minute / 60
            ] for v in self.vehicles
        ]
        print(self.vehicle_time_windows)

        # Calc total volume of each order
        for o, order in enumerate(self.orders):
            order_volume = self.calc_total_loc_volume(o + 1)
            self.orders[o]["volume"] = order_volume

        print("Data loaded")

    def request_statistics_from_api(self):
        def chunk_list(lst, chunk_size):
            """Divide a list into chunks of a given size"""
            return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

        rw = RoutingWrapper()
        dt = datetime.now()
        segments = get_objects(class_name=Segment)
        sources = []
        destinations = []
        print('Collecting incomplete road segments:', end="")
        for s, segment in enumerate(segments):
            segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])
            if len(segment_statistics) == 0:
                source = get_objects(class_name=Address, id=segment["address_1_id"])[0]
                destination = get_objects(class_name=Address, id=segment["address_2_id"])[0]
                if source not in sources:
                    sources.append(source)
                if destination not in destinations:
                    destinations.append(destination)
            if s % 1000 == 0:
                print(f"\rCollecting incomplete road segments: {s / len(segments) * 100:.0f}%", end='', flush=True)
        print('\rCollecting incomplete road segments: 100%', flush=True)

        if len(sources) == 0 or len(destinations) == 0:
            print("All segments are complete")
            return

        print("Some segments are have missing distance data, requesting from API...")

        # Divide the points into chunks of size max_sources
        source_chunks = chunk_list(sources, 50)
        # Divide the points into chunks of size max_destinations
        destination_chunks = chunk_list(destinations, 50)

        for cs, source_chunk in enumerate(source_chunks):
            for cd, destination_chunk in enumerate(destination_chunks):
                print(
                    f"Chunk {cs * len(destination_chunks) + cd + 1} of {len(source_chunks) * len(destination_chunks)}"
                )
                print('\tRequesting distances from API...', end=' ')
                chunk_sources_coords = [[a["longitude"], a["latitude"]] for a in source_chunk]
                chunk_destinations_coords = [[a["longitude"], a["latitude"]] for a in destination_chunk]
                chunk_distances, chunk_durations = rw.get_distances(chunk_sources_coords, chunk_destinations_coords)
                print('SUCCESS!')

                print('\tInserting into database...', end=' ')
                for i, source in enumerate(source_chunk):
                    for j, destination in enumerate(destination_chunk):
                        if source["id"] == destination["id"]:
                            continue
                        
                        segment = get_objects(
                            class_name=Segment, address_1_id=source["id"], address_2_id=destination["id"]
                        )[0]
                        segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])
                        
                        if len(segment_statistics) == 0:
                            insert_segment_statistics(
                                segment["id"],
                                chunk_distances[i][j],
                                chunk_durations[i][j],
                                dt.date(),
                                dt.time(),
                                dt.weekday(),
                                {'source': 'ors'}
                            )
                print('SUCCESS!')

    def create_distance_evaluator(self, addresses: list[dict]):
        def distance_evaluator(from_node, to_node):
            nonlocal addresses
            segment = get_objects(
                class_name=Segment, address_1_id=addresses[from_node]["id"], address_2_id=addresses[to_node]["id"]
            )[0]
            segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])[0]
            return segment_statistics["distance"]

        return distance_evaluator
