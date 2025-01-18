from source.domain.vrp_solver_interface import VRPSolverInterface


class GreedySolver(VRPSolverInterface):

    def initial_solution(self):
        """Initial solution for the VRP problem"""
        routes = []
        for v in range(self.vehicle_count):
            routes.append([{
                "loc": 0,
                "arrival_time": 0.0,
                "wait_time": 0.0,
                "load": 0.0
            }])
        return routes

    def travel_cost(self, from_node, to_node, current_time=None):
        # Get base distance in meters from evaluator and convert to km
        cost = float(self.distance_evaluator(from_node, to_node) / 1000)
        return cost

    def time_dependent_travel_time(self, from_node, to_node, current_time):
        base_distance = self.travel_cost(from_node, to_node)
        base_velocity = 30  # km/h
        min_velocity = 11

        if 0 <= current_time < 8:
            velocity = base_velocity
        elif 8 <= current_time < 23:
            velocity = min_velocity
        else:
            velocity = base_velocity

        travel_time = base_distance / velocity

        loc_quantity = self.demands[to_node]

        static_time = 5 / 60 if base_distance > 0 else 0  # 5 minutes
        dynamic_time = loc_quantity * 30 / 3600  # 30 seconds per product

        return travel_time + static_time + dynamic_time

    def try_add_to_route(self, route, location, current_time, vehicle_load, vehicle_capacity, vehicle_shift_end=None):
        # Calc arrival time
        arrival_time = current_time + self.time_dependent_travel_time(route[-1]["loc"], location, current_time)

        # If it's too late for the location, reject the location
        if arrival_time > self.time_windows[location][1]:
            self.lg.print(f"\tToo late for location {location}, Arrival time {arrival_time}, Right time window {self.time_windows[location][1]}")
            return current_time, vehicle_load, 0, False

        # Calc wait time in case of arrival before the left time window border
        wait_time = max(self.time_windows[location][0] - arrival_time, 0)
        current_time = arrival_time + wait_time

        # If it's now too late for the location, reject the location. Though it can't be at this point, I think
        if current_time > self.time_windows[location][1]:
            self.lg.print(f"\tToo late for location {location}, Current time {current_time}, Right time window {self.time_windows[location][1]}")
            return current_time, vehicle_load, wait_time, False

        # If it's now too late for the vehicle, reject the location also
        if vehicle_shift_end is not None and current_time > vehicle_shift_end:
            self.lg.print(f"\tToo late for location {location}, Current time {current_time}, Vehicle shift ends at {vehicle_shift_end}")
            return current_time, vehicle_load, wait_time, False

        # Calc total volume of products for the location
        loc_volume = self.demands[location] * self.volumes[location]

        # If not enough capacity to load all products for the location, reject the location
        if vehicle_load + loc_volume > vehicle_capacity:
            self.lg.print(f"\tNot enough capacity for location {location}, Vehicle load {vehicle_load}, Location volume {loc_volume}, Vehicle capacity {vehicle_capacity}")
            return current_time, vehicle_load, wait_time, False

        # If all conditions are satisfied, add load to the vehicle and append route with the location
        vehicle_load += loc_volume
        # route.append((location, current_time, vehicle_load, wait_time))
        return current_time, vehicle_load, wait_time, True

    def solve(self):
        """Greedy algorithm implementation"""
        routes = self.initial_solution()

        self.unvisited = set(range(1, len(self.locations)))
        vehicle_loads = [0] * self.vehicle_count
        vehicle_times = [0] * self.vehicle_count

        while self.unvisited:
            progress = False
            for v in range(self.vehicle_count):
                # If all locations are visited, break the loop
                if not self.unvisited:
                    break

                # Select the locations to which the vehicle can deliver all demanded products
                feasible_locations = self.select_feasible_locations(vehicle_loads, v)
                # Sort feasible locations by travel cost from current point
                feasible_locations.sort(
                    key=lambda loc: self.travel_cost(routes[v][-1]["loc"], loc, vehicle_times[v])
                )

                # Try to add the closest feasible location to the vehicle route
                for loc in feasible_locations:
                    current_time = vehicle_times[v]
                    vehicle_load = vehicle_loads[v]
                    new_time, new_load, wait_time, success = self.try_add_to_route(
                        routes[v], loc, current_time, vehicle_load, self.vehicle_capacities[v]
                    )
                    if success:
                        routes[v].append(
                            {
                                "loc": loc,
                                "arrival_time": new_time,
                                "wait_time": wait_time,
                                "load": new_load
                            }
                        )
                        vehicle_times[v] = new_time
                        vehicle_loads[v] = new_load
                        self.unvisited.remove(loc)
                        progress = True
                        self.lg.print(
                            f"Vehicle {v} added location {loc} with arrival time {new_time:.2f}, "
                            f"wait time {wait_time:.2f}, and load {new_load:.2f}"
                        )
                        break

            if not progress:
                self.lg.print("No progress made, breaking out of loop.")
                break  # Exit if no progress is made

        return routes

