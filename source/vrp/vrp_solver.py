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
        return np.linalg.norm(np.array(self.locations[from_node]) - np.array(self.locations[to_node])) * 1000

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

    def deviation_penalty(self, from_node, to_node):
        # Penal the vehicle if it's angular jumping to far away from the current location
        loc0 = self.locations[0]
        loc1 = self.locations[from_node]
        loc2 = self.locations[to_node]
        angle1 = np.arctan2(loc2[1] - loc0[1], loc2[0] - loc0[0])
        angle2 = np.arctan2(loc1[1] - loc0[1], loc1[0] - loc0[0])
        angle = abs(angle2 - angle1) % np.pi
        if angle > np.pi / 8:
            print(angle)
            return (angle - np.pi / 8) / (np.pi - np.pi / 8) * 5
        else:
            return 0

    def travel_cost(self, from_node, to_node, current_time):
        travel_time = self.time_dependent_travel_time(from_node, to_node, current_time)
        deviation_penalty = self.deviation_penalty(from_node, to_node)
        cost = travel_time + deviation_penalty
        return cost

    def initial_solution(self):
        routes = []
        for v in range(self.vehicle_count):
            routes.append([])
        return routes

    def try_add_to_route(self, route, location, current_time, vehicle_load, vehicle_capacity):
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
        # route.append((location, current_time, vehicle_load, wait_time))
        return current_time, vehicle_load, wait_time, True

    def construct_routes(self, solver="greedy"):
        if solver == "greedy":
            routes = self.construct_routes_greedy()
        elif solver == "greedy2":
            routes = self.construct_routes_greedy2()
        else:
            raise ValueError("Invalid solver specified.")
        return routes

    def construct_routes_greedy(self):
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
                    new_time, new_load, wait_time, success = self.try_add_to_route(routes[v], loc, current_time,
                                                                                   vehicle_load, self.vehicle_capacities[v])
                    routes[v].append((loc, new_time, new_load, wait_time))
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

    def construct_routes_greedy2(self):
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
                    new_time, new_load, wait_time, success = self.try_add_to_route(routes[v], loc, current_time,
                                                                                   vehicle_load,
                                                                                   self.vehicle_capacities[v])
                    routes[v].append((loc, new_time, new_load, wait_time))
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
    num_vehicles = 5
    locations = [(25, 25)] + [(random.randint(0, 50), random.randint(0, 50)) for _ in range(1, num_locations)]
    demands = [{'A': random.randint(1, 5), 'B': random.randint(1, 5)} for _ in range(num_locations)]
    demands[0] = {}  # Depot has no demand
    product_volumes = {'A': 0.07, 'B': 0.1}
    time_windows = [(0, 24)] + [(random.randint(6, 10), random.randint(18, 20)) for _ in range(num_locations - 1)]
    vehicle_capacities = [random.uniform(10, 20) for _ in range(num_vehicles)]

    cvrptw = CVRPTW(locations, demands, product_volumes, time_windows, vehicle_capacities)
    routes = cvrptw.construct_routes()
    cvrptw.print_routes(routes)

    draw = True
    if not draw:
        exit()

    import folium

    colors = [
        'red',
        'blue',
        'gray',
        'green',
        'pink',
        'darkgreen',
        'darkred',
        'lightred',
        'orange',
        'beige',
        'lightgreen',
        'darkblue',
        'lightblue',
        'purple',
        'darkpurple',
        'cadetblue',
        'lightgray',
        'black'
    ]
    m = folium.Map(location=locations[0], tiles='cartodbpositron', zoom_start=13)
    for r, route in enumerate(routes):
        route_locations = [locations[0]] + [locations[loc] for loc, _, _, _ in route] + [locations[0]]
        folium.PolyLine(route_locations, color=colors[r % len(colors)], weight=2.5, opacity=1).add_to(m)
        for i, loc in enumerate(route_locations):
            folium.Marker(loc, tooltip=f"Location {i}", icon=folium.Icon(color=colors[r % len(colors)])).add_to(m)
    m.show_in_browser()
