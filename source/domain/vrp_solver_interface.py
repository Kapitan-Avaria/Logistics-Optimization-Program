from abc import ABC, abstractmethod
from source.domain.logger_interface import LoggerInterface


class VRPSolverInterface(ABC):

    def __init__(
            self,
            locations: list,
            demands: list,
            volumes: list,
            time_windows: list,
            vehicle_capacities: list,
            vehicle_time_windows: list | None = None,
            starts: list[list[int]] = None,
            ends: list[list[int]] = None,
            distance_evaluator=None,
            logger: LoggerInterface = None
    ):
        self.locations = locations
        self.unvisited = set(range(1, len(self.locations)))
        self.demands = demands
        self.volumes = volumes
        self.time_windows = time_windows
        self.vehicle_capacities = vehicle_capacities
        self.vehicle_time_windows = vehicle_time_windows
        self.vehicle_count = len(vehicle_capacities)
        self.starts = starts if starts is not None else [[0]] * self.vehicle_count
        self.ends = ends if ends is not None else [[0]] * self.vehicle_count
        self.distance_evaluator = distance_evaluator
        self.lg = logger

    def select_feasible_locations(self, vehicle_loads, v):
        feasible_locations = [
            loc for loc in self.unvisited
            if vehicle_loads[v] + self.demands[loc] * self.volumes[loc] <= self.vehicle_capacities[v]
        ]
        return feasible_locations

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

    @abstractmethod
    def initial_solution(self):
        pass

    @abstractmethod
    def solve(self):
        pass

