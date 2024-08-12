from source.vrp.vrp_solver import CVRPTW
from source.client_1c.http_client_1c import HTTPClient1C
from source.routing.routing_wrapper import RoutingWrapper
from source.geocoding.geocoding_wrapper import GeocodingWrapper
from source.database.db_queries import *
from source.constants import DEPOT_ADDRESS

from datetime import datetime
from copy import deepcopy
import folium


class VRPWrapper:

    def __init__(self):
        self.orders = []
        self.products = dict()
        self.available_vehicles = []
        self.vehicles = []
        self.depot_address = dict()

        self.unassigned_vehicles = []
        self.unassigned_orders = []
        self.approved_routes = []
        self.actual_volume_ratio = 0.8  # A coefficient to diminish volume of the vehicle
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

    def run(self, vehicles_ids, orders_ids):
        def vehicle_index_from_vehicle_id(v_id):
            for i in range(len(self.vehicles)):
                if self.vehicles[i]["id"] == v_id:
                    return i
            raise Exception(f"Vehicle with id {v_id} not found")

        def address_index_from_order_id(o_id):
            for i in range(len(self.orders)):
                if self.orders[i]["id"] == o_id:
                    return i + 1
            raise Exception(f"Order with id {o_id} not found")

        def convert_routes(routes, locations_indices):
            converted_routes = []
            for route in routes:
                converted_route = []
                for i, point in enumerate(route):
                    converted_route.append({
                        'address': self.addresses[locations_indices[i]],
                        'arrival_time': point[1],
                        'load': point[2],
                        'wait_time': point[3]
                    })
                converted_routes.append(converted_route)
            return converted_routes

        for i, v in enumerate(self.vehicles):
            self.vehicles[i]["routes"] = []

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
            i = address_index_from_order_id(o_id)
            if self.addresses[i]["delivery_zone_type"] == "B":
                addresses_indices_b.append(i)
            elif self.addresses[i]["delivery_zone_type"] == "C":
                addresses_indices_c.append(i)

        routes_b = self.build_routes(vehicles_indices_b, addresses_indices_b)
        routes_c = self.build_routes(vehicles_indices_c, addresses_indices_c)
        routes = routes_b + routes_c

        for v in vehicles_indices_b:
            self.vehicles[v]["routes"].append(convert_routes([routes[v]], addresses_indices_b)[0])
        for v in vehicles_indices_c:
            self.vehicles[v]["routes"].append(convert_routes([routes[v]], addresses_indices_c)[0])
        self.draw_map()

    def build_routes(self, vehicles_indices, addresses_indices):
        """
        Solves CVRPTW problem for the selected vehicles and addresses
        """
        try:
            raise Exception("ORS-based distance evaluator is not stable and not invoked")
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
            distance_evaluator
        )
        routes = cvrptw.construct_routes()
        cvrptw.print_routes(routes)
        return routes

    def draw_map(self):
        """
        Draws the map with the routes
        """
        self.map = folium.Map(location=[self.depot_address["latitude"], self.depot_address["longitude"]], zoom_start=8)
        colors = [
            'red', 'blue', 'gray', 'green', 'pink', 'darkgreen', 'darkred', 'lightred', 'orange', 'beige', 'lightgreen',
            'darkblue', 'lightblue', 'purple', 'darkpurple', 'cadetblue', 'lightgray', 'black'
        ]
        routes = [v["routes"][0] for v in self.vehicles if len(v["routes"]) > 0]
        for r, route in enumerate(routes):
            route_group = folium.FeatureGroup(name=f'<span style="color: {colors[r % len(colors)]};">Route {r + 1}</span>')
            for i in range(1, len(route)):
                loc = route[i]["address"]
                marker = folium.Marker(
                    location=[loc["latitude"], loc["longitude"]],
                    tooltip=f"Location: {i}, "
                            f"Arrival Time: {route[i]['arrival_time']:.2f}, "
                            f"Load: {route[i]['load']:.2f}, "
                            f"Wait Time: {route[i]['wait_time']:.2f}",
                    icon=folium.Icon(color="blue", icon="info-sign")
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
            address = get_objects(class_name=Address, id=address["id"])
        return address

    def request_data_from_1c(self, db_is_empty, url_1c):
        """
        Loads the necessary data from 1C
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

        for o, order in enumerate(self.orders):
            # Load products and address in each order
            order_products = get_objects(class_name=OrderProduct, order_id=order["id"])
            address = get_objects(class_name=Address, id=order["address_id"])[0]
            if self.request_coords_on_load:
                address = self.reload_address_if_not_geocoded(address)
            delivery_zone_type = get_objects(class_name=DeliveryZone, id=address["delivery_zone_id"])[0]["type"]
            address["delivery_zone_type"] = delivery_zone_type

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

        random_zone = get_objects(class_name=DeliveryZone, id=self.orders[0]["address"]["delivery_zone_id"])[0]
        try:
            self.depot_address = get_objects(class_name=Address, id=random_zone["depot_id"])[0]
        except IndexError:
            print("[WARN]: Depot address was not loaded, inserting default")
            self.depot_address = get_objects(class_name=Address, string_address=DEPOT_ADDRESS)[0]

        self.unassigned_vehicles = [i for i in range(len(self.vehicles))]
        self.unassigned_orders = [i for i in range(len(self.orders))]

        # ***************************
        # Prepare VRP data
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

        print("Data loaded")

    def create_distance_evaluator(self, addresses):
        """
        Calculates 'matrices' of distances and durations between all nodes in the zone.
        :param addresses: list of addresses
        :return: evaluator function
        """
        distances = []
        segments = []
        lack_of_data = False

        # Load all segments from the db
        for i, from_node in enumerate(addresses):
            segments.append([])
            for j, to_node in enumerate(addresses):
                if i == j:
                    segments[i].append(None)
                    continue
                segment = get_objects(
                    class_name=Segment, address_1_id=from_node["id"], address_2_id=to_node["id"]
                )[0]
                segments[i].append(segment)
                segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])
                num_records = len(segment_statistics)
                if num_records == 0:
                    lack_of_data = True

        # If there is no data for some of the segments, request distances from routing API
        if lack_of_data:
            locations = [[a["longitude"], a["latitude"]] for a in addresses]
            rw = RoutingWrapper()
            dist, dur = rw.get_distances(locations)
            dt = datetime.now()

        for i, from_node in enumerate(addresses):
            distances.append([])
            for j, to_node in enumerate(addresses):
                if i == j:
                    distances[i].append(0)
                    continue

                segment = segments[i][j]

                if lack_of_data:
                    insert_segment_statistics(
                        segment["id"],
                        dist[i][j],
                        dur[i][j],
                        dt.date(),
                        dt.time(),
                        dt.weekday(),
                        {'source': 'ors'}
                    )

                # Calculate average distance and duration between the two nodes
                segment_statistics = get_objects(class_name=SegmentStatistics, segment_id=segment["id"])
                num_records = len(segment_statistics)

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

