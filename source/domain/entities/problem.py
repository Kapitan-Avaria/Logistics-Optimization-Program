from dataclasses import dataclass


@dataclass
class Problem:
    locations: list
    demands: list
    volumes: list
    time_windows: list
    vehicle_capacities: list
    vehicle_time_windows: list


