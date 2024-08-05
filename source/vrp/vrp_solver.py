import numpy as np
import random


class CVRPTW:
    def __init__(self, locations, demands, product_volumes, time_windows, vehicle_capacities, distance_evaluator=None):
        self.locations = locations
        self.demands = demands
        self.product_volumes = product_volumes
        self.time_windows = time_windows
        self.vehicle_capacities = vehicle_capacities
        self.vehicle_count = len(vehicle_capacities)
        self.calc_base_distance = self.default_distance_evaluator if distance_evaluator is None else distance_evaluator

    def default_distance_evaluator(self, from_node, to_node):
        return np.linalg.norm(np.array(self.locations[from_node]) - np.array(self.locations[to_node]))

    def time_dependent_travel_time(self, from_node, to_node, current_time):
        base_distance = self.calc_base_distance(from_node, to_node) / 1000  # Converting to kilometers
        base_velocity = 30  # km/h
        min_velocity = 11

        # Define traffic conditions
        if 0 <= current_time < 6:
            velocity = base_velocity
        elif 6 <= current_time < 8:
            velocity = base_velocity * (min_velocity - base_velocity) / 2 + 87
        elif 8 <= current_time < 17:
            velocity = min_velocity
        elif 17 <= current_time < 23:
            velocity = base_velocity * (base_velocity - min_velocity) / 6 - 42.84
        else:
            velocity = base_velocity

        return base_distance / velocity

    def travel_cost(self, from_node, to_node, current_time):
        cost = self.time_dependent_travel_time(from_node, to_node, current_time)
        return cost

    def initial_solution(self):
        routes = []
        for v in range(self.vehicle_count):
            routes.append([])
        return routes

    def add_to_route(self, route, location, current_time, vehicle_load, vehicle_capacity):
        # Calc arrival time
        if not route:
            arrival_time = self.time_dependent_travel_time(0, location, current_time)
        else:
            arrival_time = current_time + self.time_dependent_travel_time(route[-1][0], location, current_time)

        # If it's too late for the location, reject the location
        if arrival_time > self.time_windows[location][1]:
            return current_time, vehicle_load, 0, False

        # Calc wait time in case of arrival before the left time window border
        wait_time = max(self.time_windows[location][0] - arrival_time, 0)
        current_time = arrival_time + wait_time

        # If it's now too late for the location, reject the location. Though it can't be at this point, I think
        if current_time > self.time_windows[location][1]:
            return current_time, vehicle_load, wait_time, False

        # Calc total volume of products for the location
        total_volume = 0
        for product, quantity in self.demands[location].items():
            total_volume += quantity * self.product_volumes[product]

        # If not enough capacity to load all products for the location, reject the location
        if vehicle_load + total_volume > vehicle_capacity:
            return current_time, vehicle_load, wait_time, False

        # If all conditions are satisfied, add load to the vehicle and append route with the location
        vehicle_load += total_volume
        route.append((location, current_time, vehicle_load, wait_time))
        return current_time, vehicle_load, wait_time, True

    def construct_routes(self):
        routes = self.initial_solution()
        unvisited = set(range(1, len(self.locations)))
        vehicle_loads = [0] * self.vehicle_count
        vehicle_times = [0] * self.vehicle_count

        while unvisited:
            progress = False
            for v in range(self.vehicle_count):
                # If all locations are visited, break the loop
                if not unvisited:
                    break

                # Select the locations to which the vehicle can deliver all demanded products
                feasible_locations = [
                    loc for loc in unvisited
                    if vehicle_loads[v] + sum(
                        self.demands[loc][product] * self.product_volumes[product] for product in self.demands[loc]) <=
                       self.vehicle_capacities[v]
                ]
                # Sort feasible locations by travel cost from current point
                feasible_locations.sort(
                    key=lambda loc: self.travel_cost(routes[v][-1][0], loc, vehicle_times[v]) if routes[v]
                    else self.travel_cost(0, loc, vehicle_times[v])
                )

                # Try to add the closest feasible location to the vehicle route
                for loc in feasible_locations:
                    current_time = vehicle_times[v]
                    vehicle_load = vehicle_loads[v]
                    new_time, new_load, wait_time, success = self.add_to_route(routes[v], loc, current_time,
                                                                               vehicle_load, self.vehicle_capacities[v])
                    if success:
                        vehicle_times[v] = new_time
                        vehicle_loads[v] = new_load
                        unvisited.remove(loc)
                        progress = True
                        print(
                            f"Vehicle {v + 1} added location {loc} with arrival time {new_time:.2f}, "
                            f"wait time {wait_time:.2f}, and load {new_load:.2f}")
                        break

            if not progress:
                print("No progress made, breaking out of loop.")
                break  # Exit if no progress is made

        return routes

    def print_routes(self, routes):
        for v, route in enumerate(routes):
            print(f"\nVehicle {v + 1} Route:")
            for loc, arrival_time, load, wait_time in route:
                print(
                    f"  Location: {loc}, Arrival Time: {arrival_time:.2f}, Load: {load:.2f}, Wait Time: {wait_time:.2f}")
            print(f"  Return to depot")


if __name__ == "__main__":
    # Generate Example Data
    random.seed(42)
    num_locations = 50
    num_vehicles = 10
    locations = [(random.randint(0, 50), random.randint(0, 50)) for _ in range(num_locations)]
    demands = [{'A': random.randint(1, 5), 'B': random.randint(1, 5)} for _ in range(num_locations)]
    demands[0] = {}  # Depot has no demand
    product_volumes = {'A': 0.07, 'B': 0.1}
    time_windows = [(0, 24)] + [(random.randint(6, 10), random.randint(18, 20)) for _ in range(num_locations - 1)]
    vehicle_capacities = [random.uniform(10, 20) for _ in range(num_vehicles)]

    cvrptw = CVRPTW(locations, demands, product_volumes, time_windows, vehicle_capacities)
    routes = cvrptw.construct_routes()
    cvrptw.print_routes(routes)
