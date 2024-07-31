from source.vrp.vrp_solver import CVRPTW
from source.client_1c.http_client_1c import HTTPClient1C
from source.database.db_queries import *


class VRPWrapper:
    orders: list
    products: dict
    vehicles: list
    depot_address: dict

    def __init__(self, db_is_empty, url_1c):
        self.db_is_empty = db_is_empty
        self.url_1c = url_1c
        self.load_data()

        num_orders = len(self.orders)

        locations = [(self.depot_address["longitude"], self.depot_address["latitude"])] + [
            (self.orders[o]["address"]["longitude"], self.orders[o]["address"]["latitude"]) for o in range(num_orders)
        ]
        demands = [{}] + [
            {p["product_id"]: p["quantity"] for p in self.orders[o]["products"]} for o in range(num_orders)
        ]
        product_volumes = {p["product_id"]: p["volume"] for p in self.products}
        time_windows = [(0, 24)] + [self.orders[o] for o in range(num_orders)]
        vehicle_capacities = [v["dimensions"]["inner"]["volume"] for v in self.vehicles]

        cvrptw = CVRPTW(locations, demands, product_volumes, time_windows, vehicle_capacities)
        routes = cvrptw.construct_routes()
        cvrptw.print_routes(routes)

    def load_data(self):
        """
        Loads the necessary data from 1C and from the local db
        """
        client = HTTPClient1C(self.url_1c)

        # Load historical and utility data from 1C if database was created in the first time
        if self.db_is_empty:
            all_products = client.get_all_products()
            insert_products(all_products)

            all_vehicles = client.get_all_vehicles()
            insert_vehicles(all_vehicles)

            archived_orders = client.get_archived_orders()
            insert_orders(archived_orders)

            # all_vehicle_geodata = client1c.get_vehicles_geodata()
            self.db_is_empty = False

        # Load operational data from 1C
        # Load available orders to the database
        available_orders = client.get_available_orders()
        insert_orders(available_orders)

        # Load available vehicles from 1C
        available_vehicles = client.get_available_vehicles()
        # insert_vehicles(available_vehicles)
        # TODO: добавить обращение по имени каждой машины, которой ещё нет в базе, добавление в базу

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
