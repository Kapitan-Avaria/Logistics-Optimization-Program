import numpy as np
import random
import folium


class CVRPTW:
    def __init__(
            self,
            locations,
            demands,
            product_volumes,
            time_windows,
            vehicle_capacities,
            vehicle_time_windows=None,
            distance_evaluator=None,
            loc_clusters=None
    ):
        self.locations = locations
        self.demands = demands
        self.product_volumes = product_volumes
        self.time_windows = time_windows
        self.vehicle_capacities = vehicle_capacities
        self.vehicle_time_windows = vehicle_time_windows
        self.vehicle_count = len(vehicle_capacities)
        self.calc_base_distance = self.default_distance_evaluator if distance_evaluator is None else distance_evaluator
        self.loc_clusters = loc_clusters

    def default_distance_evaluator(self, from_node, to_node):
        return np.linalg.norm(np.array(self.locations[from_node]) - np.array(self.locations[to_node])) * 1000

    def travel_distance(self, from_node, to_node):
        return float(self.calc_base_distance(from_node, to_node) / 1000)  # Converting to kilometers

    def time_dependent_travel_time(self, from_node, to_node, current_time):
        base_distance = self.travel_distance(from_node, to_node)
        base_velocity = 30  # km/h
        min_velocity = 11

        # Define traffic conditions
        # if 0 <= current_time < 6:
        #     velocity = base_velocity
        # elif 6 <= current_time < 8:
        #     velocity = base_velocity * (min_velocity - base_velocity) / 2 + 87
        # elif 8 <= current_time < 17:
        #     velocity = min_velocity
        # elif 17 <= current_time < 23:
        #     velocity = base_velocity * (base_velocity - min_velocity) / 6 - 42.84
        # else:
        #     velocity = base_velocity

        if 0 <= current_time < 8:
            velocity = base_velocity
        elif 8 <= current_time < 23:
            velocity = min_velocity
        else:
            velocity = base_velocity

        travel_time = base_distance / velocity

        loc_quantity = sum(self.demands[to_node].values())

        static_time = 5 / 60  # 5 minutes
        dynamic_time = loc_quantity * 30 / 3600  # 30 seconds per product

        return travel_time + static_time + dynamic_time

    def predistribute_sectors(self):

        def calculate_angle(location, center):
            dx = location[0] - center[0]
            dy = location[1] - center[1]
            angle = np.arctan2(float(dy), float(dx))
            return angle

        loc_indices = [i for i in range(1, len(self.locations))]
        angles = [0] + [calculate_angle(self.locations[p], self.locations[0]) for p in range(1, len(self.locations))]

        # Sort points by angle from the center
        loc_indices.sort(key=lambda p: calculate_angle(self.locations[p], self.locations[0]))
        # Initialize sectors
        sectors = [[] for _ in range(len(self.vehicle_capacities) + 1)]

        # Distribute points to sectors
        current_sector = 0
        current_sector_start_angle = angles[loc_indices[0]]
        current_capacity = self.vehicle_capacities[current_sector]
        current_volume = 0

        for loc in loc_indices:

            # Calc total volume of products for the location
            loc_volume = 0
            for product, quantity in self.demands[loc].items():
                loc_volume += quantity * self.product_volumes[product]

            if current_volume + loc_volume <= current_capacity and abs(angles[loc] - current_sector_start_angle) <= np.pi / 2:
                # Add the point to the current sector
                sectors[current_sector].append(loc)
                current_volume += loc_volume
            else:
                current_sector_start_angle = angles[loc]
                current_sector += 1
                if current_sector < len(self.vehicle_capacities):
                    current_capacity = self.vehicle_capacities[current_sector]
                    current_volume = loc_volume
                    sectors[current_sector].append(loc)
                else:
                    break

        return sectors

    def travel_cost(self, from_node, to_node, current_time):
        travel_distance = self.travel_distance(from_node, to_node)
        # travel_time = self.time_dependent_travel_time(from_node, to_node, current_time)
        # wait_time = max(self.time_windows[to_node][0] - (current_time + travel_time), 0)
        # cost = travel_time + wait_time  # + deviation_penalty
        cost = travel_distance
        return cost

    def initial_solution(self):
        routes = []
        for v in range(self.vehicle_count):
            routes.append([])
        return routes

    def calculate_route_time(self, route):
        current_time = 0
        total_time = 0
        for i in range(len(route)):
            if i == 0:
                current_time = self.time_windows[route[i][0]][0]
            else:
                current_time = self.try_add_to_route(route[:i], route[i][0], current_time, 0, self.vehicle_capacities[0])[0]
            total_time = current_time
        return total_time

    def update_route_params(self, route):
        current_time = 0
        vehicle_load = 0
        for i in range(len(route)):
            if i == 0:
                current_time = self.time_windows[route[i][0]][0]
                vehicle_load = 0
            else:
                current_time, vehicle_load, wait_time, success = self.try_add_to_route(route[:i], route[i][0], current_time, vehicle_load, self.vehicle_capacities[0])
                if success:
                    route[i] = (route[i][0], current_time, vehicle_load, wait_time)
                else:
                    # Route is not possible
                    return False
        return route

    # def improve_route(self, route):
    #     best_route = route
    #     best_time = route[-1][1]
    #     for i in range(2, len(route)):
    #         for j in range(i + 1, len(route)):
    #             new_route = deepcopy(best_route)
    #             new_route[i:j] = new_route[i:j][::-1]
    #             new_route = self.update_route_params(new_route)
    #             if not new_route:
    #                 continue
    #
    #             new_time = new_route[-1][1]
    #             if new_time < best_time:
    #                 best_route = new_route
    #                 best_time = new_time
    #
    #     return best_route

    def try_add_to_route(self, route, location, current_time, vehicle_load, vehicle_capacity, vehicle_shift_end=None):
        # Calc arrival time
        if not route:
            arrival_time = self.time_dependent_travel_time(0, location, current_time)
        else:
            arrival_time = current_time + self.time_dependent_travel_time(route[-1][0], location, current_time)

        # If it's too late for the location, reject the location
        if arrival_time > self.time_windows[location][1]:
            print(f"\tToo late for location {location}, Arrival time {arrival_time}, Right time window {self.time_windows[location][1]}")
            return current_time, vehicle_load, 0, False

        # Calc wait time in case of arrival before the left time window border
        wait_time = max(self.time_windows[location][0] - arrival_time, 0)
        current_time = arrival_time + wait_time

        # If it's now too late for the location, reject the location. Though it can't be at this point, I think
        if current_time > self.time_windows[location][1]:
            print(f"\tToo late for location {location}, Current time {current_time}, Right time window {self.time_windows[location][1]}")
            return current_time, vehicle_load, wait_time, False

        # If it's now too late for the vehicle, reject the location also
        if vehicle_shift_end is not None and current_time > vehicle_shift_end:
            print(f"\tToo late for location {location}, Current time {current_time}, Vehicle shift ends at {vehicle_shift_end}")
            return current_time, vehicle_load, wait_time, False

        # Calc total volume of products for the location
        total_volume = 0
        for product, quantity in self.demands[location].items():
            total_volume += quantity * self.product_volumes[product]

        # If not enough capacity to load all products for the location, reject the location
        if vehicle_load + total_volume > vehicle_capacity:
            print(f"\tNot enough capacity for location {location}, Vehicle load {vehicle_load}, Location volume {total_volume}, Vehicle capacity {vehicle_capacity}")
            return current_time, vehicle_load, wait_time, False

        # If all conditions are satisfied, add load to the vehicle and append route with the location
        vehicle_load += total_volume
        # route.append((location, current_time, vehicle_load, wait_time))
        return current_time, vehicle_load, wait_time, True

    def construct_routes(self, solver="clustered_seq", start_from_farthest=False):
        if solver == "greedy":
            routes = self.construct_routes_greedy(use_predistributed_sectors=False)
        elif solver == "greedy2":
            routes = self.construct_routes_greedy(use_predistributed_sectors=True)
        elif solver == "clustered":
            if self.loc_clusters is None:
                raise ValueError("Clustered solver requires loc_clusters to be provided.")
            routes = self.construct_routes_clustered(start_from_farthest=start_from_farthest)
        elif solver == "clustered_seq":
            if self.loc_clusters is None:
                raise ValueError("Clustered solver requires loc_clusters to be provided.")
            routes = self.construct_routes_clustered_sequential(start_from_farthest=start_from_farthest)
        else:
            raise ValueError("Invalid solver specified.")
        # routes = [self.improve_route(route) if len(route) > 0 else route for route in routes]
        return routes

    def select_feasible_locations(self, unvisited, vehicle_loads, v, subsets=None):
        if subsets is not None:
            other_subsets = [s for i, s in enumerate(subsets) if i != v]
            forbidden_locations = [loc for subset in other_subsets for loc in subset]
        else:
            forbidden_locations = []

        feasible_locations = [
            loc for loc in unvisited
            if vehicle_loads[v] + sum(
                self.demands[loc][product] * self.product_volumes[product] for product in self.demands[loc]) <=
               self.vehicle_capacities[v] and (loc in subsets[v] if subsets[v] else True) and (loc not in forbidden_locations)
        ]
        return feasible_locations

    def construct_routes_greedy(self, use_predistributed_sectors=True):
        routes = self.initial_solution()
        unvisited = set(range(1, len(self.locations)))
        vehicle_loads = [0] * self.vehicle_count
        vehicle_times = [0] * self.vehicle_count

        if use_predistributed_sectors:
            sectors = self.predistribute_sectors()
        else:
            sectors = []
            for v in range(self.vehicle_count):
                sectors.append(set())

        while unvisited:
            progress = False
            for v in range(self.vehicle_count):
                # If all locations are visited, break the loop
                if not unvisited:
                    break

                # Select the locations to which the vehicle can deliver all demanded products
                feasible_locations = self.select_feasible_locations(unvisited, vehicle_loads, v, sectors)
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
                    if success:
                        routes[v].append((loc, new_time, new_load, wait_time))
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

    def construct_routes_clustered(self, start_from_farthest=False):
        routes = self.initial_solution()
        unvisited = set(range(1, len(self.locations)))
        vehicle_loads = [0] * self.vehicle_count
        vehicle_times = [0] * self.vehicle_count

        subsets: list[set[int]] = []
        for v in range(self.vehicle_count):
            subsets.append(set())

        def select_from_same_cluster(loc):
            cluster = set()
            for loc2 in unvisited:
                if self.loc_clusters[loc2] == self.loc_clusters[loc]:
                    cluster.add(loc2)
            return cluster

        k = 0
        while unvisited:
            progress = False
            k += 1
            for v in range(self.vehicle_count):
                # If all locations are visited, break the loop
                if not unvisited:
                    break

                # Select the locations to which the vehicle can deliver all demanded products
                feasible_locations = self.select_feasible_locations(unvisited, vehicle_loads, v, subsets)
                # Sort feasible locations by travel cost from current point
                feasible_locations.sort(
                    key=lambda loc: self.travel_cost(routes[v][-1][0], loc, vehicle_times[v]) if routes[v]
                    else self.travel_cost(0, loc, vehicle_times[v]),
                    reverse=True if (start_from_farthest and k == 1) else False
                )

                # Try to add the closest feasible location to the vehicle route
                for loc in feasible_locations:
                    current_time = vehicle_times[v]
                    vehicle_load = vehicle_loads[v]
                    new_time, new_load, wait_time, success = self.try_add_to_route(routes[v], loc, current_time,
                                                                                   vehicle_load,
                                                                                   self.vehicle_capacities[v])
                    if success:
                        routes[v].append((loc, new_time, new_load, wait_time))
                        vehicle_times[v] = new_time
                        vehicle_loads[v] = new_load

                        if not subsets[v]:
                            subsets[v] = select_from_same_cluster(loc)
                        unvisited.remove(loc)
                        subsets[v].remove(loc)

                        progress = True
                        print(
                            f"Vehicle {v + 1} added location {loc} with arrival time {new_time:.2f}, "
                            f"wait time {wait_time:.2f}, and load {new_load:.2f}")
                        break
            if not progress:
                print("No progress made, breaking out of loop.")
                break  # Exit if no progress is made

        return routes

    def construct_routes_clustered_sequential(self, start_from_farthest=False):
        routes = self.initial_solution()
        unvisited = set(range(1, len(self.locations)))
        vehicle_loads = [0] * self.vehicle_count
        vehicle_times = [tw[0] for tw in self.vehicle_time_windows]  # Start from the earliest possible time

        subsets: list[set[int]] = []
        for v in range(self.vehicle_count):
            subsets.append(set())

        def select_from_same_cluster(loc):
            cluster = set()
            for loc2 in unvisited:
                if self.loc_clusters[loc2] == self.loc_clusters[loc]:
                    cluster.add(loc2)
            return cluster

        for v in range(self.vehicle_count):
            k = 0
            while unvisited:
                progress = False
                k += 1

                # If all locations are visited, break the loop
                if not unvisited:
                    break

                # Select the locations to which the vehicle can deliver all demanded products
                feasible_locations = self.select_feasible_locations(unvisited, vehicle_loads, v, subsets)
                # Sort feasible locations by travel cost from current point
                feasible_locations.sort(
                    key=lambda loc: self.travel_cost(routes[v][-1][0], loc, vehicle_times[v]) if routes[v]
                    else self.travel_cost(0, loc, vehicle_times[v]),
                    reverse=True if (start_from_farthest and k == 1) else False
                )

                # Try to add the closest feasible location to the vehicle route
                for loc in feasible_locations:
                    current_time = vehicle_times[v]
                    vehicle_load = vehicle_loads[v]
                    new_time, new_load, wait_time, success = self.try_add_to_route(
                        routes[v], loc, current_time, vehicle_load,
                        self.vehicle_capacities[v], self.vehicle_time_windows[v][1]
                    )
                    if success:
                        routes[v].append((loc, new_time, new_load, wait_time))
                        vehicle_times[v] = new_time
                        vehicle_loads[v] = new_load

                        if not subsets[v]:
                            subsets[v] = select_from_same_cluster(loc)
                        unvisited.remove(loc)
                        subsets[v].remove(loc)

                        progress = True
                        print(
                            f"Vehicle {v + 1} added location {loc} with delivery time {new_time:.2f}, "
                            f"wait time {wait_time:.2f}, and load {new_load:.2f}")
                        break
                if not progress:
                    subsets[v] = set()  # Release occupied locations
                    print("No progress made, go to next vehicle")
                    break  # Go to next vehicle

        return routes

    def print_routes(self, routes):
        for v, route in enumerate(routes):
            print(f"\nVehicle {v + 1}. Capacity: {self.vehicle_capacities[v]}. Route:")
            for loc, arrival_time, load, wait_time in route:
                print(
                    f"  Location: {loc}, Arrival Time: {arrival_time:.2f}, Load: {load:.2f}, Wait Time: {wait_time:.2f}")
            print(f"  Return to depot")

    def draw_routes(self, locations, routes):
        colors = [
            'red', 'blue', 'gray', 'green', 'pink', 'darkgreen', 'darkred', 'lightred', 'orange', 'beige', 'lightgreen',
            'darkblue', 'lightblue', 'purple', 'darkpurple', 'cadetblue', 'lightgray', 'black'
        ]
        m = folium.Map(location=locations[0], tiles='cartodbpositron', zoom_start=13)
        for r, route in enumerate(routes):
            route_locations = [locations[0]] + [locations[loc] for loc, _, _, _ in route] + [locations[0]]
            folium.PolyLine(route_locations, color=colors[r % len(colors)], weight=2.5, opacity=1).add_to(m)
            for i, loc in enumerate(route_locations):
                folium.Marker(loc, tooltip=f"Location {i}", icon=folium.Icon(color=colors[r % len(colors)])).add_to(m)
        m.show_in_browser()


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
    # time_windows = [(0, 24)] + [(8, 18) for _ in range(num_locations - 1)]
    vehicle_capacities = [random.uniform(10, 20) for _ in range(num_vehicles)]

    cvrptw = CVRPTW(locations, demands, product_volumes, time_windows, vehicle_capacities)
    routes = cvrptw.construct_routes('greedy2')
    cvrptw.print_routes(routes)

    draw = True
    if draw:
        cvrptw.draw_routes(locations, routes)
