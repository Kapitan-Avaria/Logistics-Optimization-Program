import numpy as np

from source.domain.delivery_planner_interface import DeliveryPlannerInterface
from source.domain.vrp_solver_interface import VRPSolverInterface
from source.solvers.greedy_solver import GreedySolver
from source.solvers.distance_evaluators import create_distance_evaluator_from_data, create_euclidian_distance_evaluator

from source.domain.entities import *


class DeliveryPlanner(DeliveryPlannerInterface):

    def two_step_strategy(self, areas):
        # Consider all the areas separately
        for area in areas:
            depot_address = area["depot_address"]
            orders = area["orders"]
            order_products = area["order_products"]
            delivery_zones = area["delivery_zones"]
            addresses = area["addresses"]
            vehicles = area["vehicles"]

            # Build inter-zone problems
            locations_b = [(depot_address.latitude, depot_address.longitude)]
            volumes_b = [0]
            locations_c = [(depot_address.latitude, depot_address.longitude)]
            volumes_c = [0]

            # Find the centroids of each zone
            # Sum all the volumes of each zone
            for dz in delivery_zones:
                centroid = np.array([0, 0])
                zone_volume = 0
                zone_size = 0
                for o, order in enumerate(orders):
                    if order.delivery_zone_id != dz.id:
                        continue
                    centroid += np.array([addresses[o].latitude, addresses[o].longitude])
                    for op in order_products[o]:
                        zone_volume += op   # considering each op in this case is just volume value
                    zone_size += 1

                if dz.type == "B":
                    locations_b.append(
                        [centroid[0] / zone_size,
                         centroid[1] / zone_size]
                    )
                    volumes_b.append(zone_volume)

                else:
                    locations_c.append(
                        [centroid[0] / zone_size,
                         centroid[1] / zone_size]
                    )
                    volumes_c.append(zone_volume)

            def build_inter_zone_problem(locations, volumes, vehicle_capacities):
                problem = Problem(
                    locations=locations,
                    demands=[0] + [1] * (len(locations) - 1),
                    volumes=volumes,
                    time_windows=[(0, 24)] * len(locations),
                    vehicle_capacities=vehicle_capacities,
                    vehicle_time_windows=[(0, 24)] * len(vehicle_capacities),
                    distance_evaluator=create_euclidian_distance_evaluator(locations)
                )
                return problem

            problem_b = build_inter_zone_problem(
                locations_b, volumes_b, [vehicle.volume_capacity for vehicle in vehicles if vehicle.type == "B"]
            )
            problem_c = build_inter_zone_problem(
                locations_c, volumes_c, [vehicle.volume_capacity for vehicle in vehicles if vehicle.type == "C"]
            )

            routes_b = self.build_routes(problem_b, GreedySolver)
            routes_c = self.build_routes(problem_c, GreedySolver)

            # Solve inter-zone problem
            pass

        # Solve problems inside each zone

        # Merge routes

        # Optimize resulting route

        """locations.append((depot_address.latitude, depot_address.longitude))
        addresses.append(depot_address)
        time_windows.append((0, 24))
        for o, order in enumerate(orders):
            order_products = self.db.get_order_products(order.id)
            for op in order_products:
                address = self.db.get_address(order.address_id)
                locations.append((address.latitude, address.longitude))
                addresses.append(address)
                demands.append(op.quantity)
                volumes.append(self.db.get_product(op.product_id).volume)
                ts = order.delivery_time_start
                te = order.delivery_time_end
                time_windows.append((ts.hour + ts.minute / 60, te.hour + te.minute / 60))

        vehicles = self.db.get_vehicles()
        for v, vehicle in enumerate(vehicles):
            vehicle_capacities.append(vehicle.dimensions)
            vehicle_time_windows.append((0, 24))"""
        pass

    def export_routes(self):
        pass

    def build_routes(self, problem: Problem, SolverClass):
        solver = SolverClass(
            problem.locations,
            problem.demands,
            problem.volumes,
            problem.time_windows,
            problem.vehicle_capacities,
            problem.vehicle_time_windows,
            problem.distance_evaluator
        )
        return solver.solve()

    def edit_route(self):
        pass
