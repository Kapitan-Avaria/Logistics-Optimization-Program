from source.domain.data_business_interface import BusinessDataInterface
from source.domain.database_interface import DatabaseInterface
from source.domain.data_geocoding_interface import GeoDataInterface
from source.domain.data_routing_interface import RoutingDataInterface
from source.domain.entities import *


class DataOperator:
    def __init__(
            self,
            db: DatabaseInterface,
            business_data: BusinessDataInterface,
            geo_data: GeoDataInterface,
            routing_data: RoutingDataInterface
    ):
        self.db = db
        self.business_data = business_data
        self.geo_data = geo_data
        self.routing_data = routing_data

    def load_data_from_business_to_db(self, start_date=None, end_date=None):
        """Request all the products, vehicles and available orders with all corresponding data
        from the business data source and load to the db"""

        all_products = self.business_data.get_all_products()
        all_vehicles = self.business_data.get_all_vehicles()
        available_orders = self.business_data.get_available_orders(start_date, end_date)

        # Upserting products to the db
        for p, product in enumerate(all_products):
            # This and the following similar constructions inside entity constructor calls
            # are needed to ignore excessive fields in structures from the business data source
            # which are not needed in the db
            self.db.upsert_product(Product(**{k: all_products[p][k] for k in Product.__annotations__.keys()}))

        # Upserting vehicles to the db
        for v, vehicle in enumerate(all_vehicles):
            self.db.upsert_vehicle(Vehicle(**{k: all_vehicles[v][k] for k in Vehicle.__annotations__.keys()}))

        # The 'depots' set is for storing the ids of depots which was found in orders structure
        # This is for making sure the address of a depot is requested only once
        depots = set()
        # Parsing the orders and upserting addresses and orders to the db
        for o, order in enumerate(available_orders):
            depot_id = available_orders[o]["depot_id"]
            if depot_id not in depots:
                depot_address = self.business_data.get_depot(available_orders[o]["depot_id"])
                depots.add(depot_id)
                if depot_address:
                    self.db.upsert_address(Address(**{k: depot_address[k] for k in Address.__annotations__.keys()}))
            self.db.upsert_order(Order(**{k: available_orders[o][k] for k in Order.__annotations__.keys()}))

    def load_data_from_geocoding_to_db(self):
        """Request all the addresses from the db and geocode them using the geocoding data source"""
        addresses = self.db.get_ungeocoded_addresses()
        for a, address in enumerate(addresses):
            address.latitude, address.longitude = self.geo_data.geocode(address.machine_address)
            self.db.upsert_address(address)

    def load_data_from_routing_to_db(self, addresses_ids=None, only_unrouted=True):
        """Request all the unrouted segments from the db and get the routing data using the routing data source"""
        # If true, only segments without statistical data will be requested from the db
        # If false, all segments will be requested from the db
        if only_unrouted:
            segments = self.db.get_unrouted_segments(addresses_ids)
        else:
            segments = self.db.get_segments(addresses_ids)

        for s, segment in enumerate(segments):
            source = self.db.get_address(segment.address_1_id)
            destination = self.db.get_address(segment.address_2_id)
            segment_data = self.routing_data.get_segment_data(
                (source.latitude, source.longitude),
                (destination.latitude, destination.longitude),
                segment.id
            )
            self.db.insert_segment_statistics(SegmentStatistics(**segment_data))

    def from_db(self):
        """Loads and builds the transportation problem data from the db"""
        locations: list = []
        demands: list = [0]
        volumes: list = [0]
        time_windows: list = []
        vehicle_capacities: list = []
        vehicle_time_windows: list = []

        orders = self.db.get_orders(status=0)
        depot_address = self.db.get_address(self.db.get_delivery_zone(orders[0].delivery_zone_id).depot_id)
        locations.append((depot_address.latitude, depot_address.longitude))
        time_windows.append((0, 24))
        for o, order in enumerate(orders):
            order_products = self.db.get_order_products(order.id)
            for op in order_products:
                address = self.db.get_address(order.address_id)
                locations.append((address.latitude, address.longitude))
                demands.append(op.quantity)
                volumes.append(self.db.get_product(op.product_id).volume)
                ts = order.delivery_time_start
                te = order.delivery_time_end
                time_windows.append((ts.hour + ts.minute / 60, te.hour + te.minute / 60))

        vehicles = self.db.get_vehicles()
        for v, vehicle in enumerate(vehicles):
            vehicle_capacities.append(vehicle.dimensions)
            vehicle_time_windows.append((0, 24))

        return Problem(
            locations=locations,
            demands=demands,
            volumes=volumes,
            time_windows=time_windows,
            vehicle_capacities=vehicle_capacities,
            vehicle_time_windows=vehicle_time_windows
        )
