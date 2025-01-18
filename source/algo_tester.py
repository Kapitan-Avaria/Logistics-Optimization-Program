"""Script for testing solvers and gathering statistics"""
import random
import numpy as np
from scipy.spatial import distance_matrix as dm
from source.solvers.greedy_solver import GreedySolver
from source.solvers.ant_colony_solver import AntColonySolver
from time import time
import pandas as pd
from source.loggers.logger import Logger


def generate_test_case(
        num_locations=20,
        num_vehicles=5,
        depot_location=(0, 0),
        area_size=50,  # km
        max_demand=10,
        max_volume=2,  # cubic meters
        vehicle_capacity=30,
        time_window_span=12  # Length of the time period, in which delivery is possible
):
    """
    Generate test data for the VRP problem.

    Args:
        num_locations: Number of delivery locations (excluding depot)
        num_vehicles: Number of available vehicles
        depot_location: (x, y) coordinates of the depot
        area_size: Size of the square area in kilometers
        max_demand: Maximum demand per location
        max_volume: Maximum volume per item
        vehicle_capacity: Capacity of each vehicle
        time_window_span: Time window span in hours
    """
    # Generate random locations
    locations = [[depot_location[0], depot_location[1]]]  # Start with depot
    for _ in range(num_locations):
        x = random.uniform(-area_size / 2, area_size / 2)
        y = random.uniform(-area_size / 2, area_size / 2)
        locations.append([x, y])

    # Generate demands (depot has no demand)
    demands = [0]  # Depot demand
    for _ in range(num_locations):
        demands.append(random.randint(1, max_demand))

    # Generate volumes
    volumes = [0]  # Depot volume
    for _ in range(num_locations):
        volumes.append(random.uniform(0.1, max_volume))

    if time_window_span is None:
        time_windows = [(0, 10000000000) for _ in range(num_locations + 1)]
    else:
        # Generate time windows
        time_windows = [(0, 24)]  # Depot is always open
        for _ in range(num_locations):
            start = random.uniform(0, 24 - time_window_span)
            end = min(start + time_window_span, 24)
            time_windows.append((start, end))

    # distance_matrix = dm(locations, locations)
    vehicle_capacities = [vehicle_capacity] * num_vehicles

    def distance_evaluator(from_index, to_index):
        dist = np.linalg.norm(np.array(locations[from_index]) - np.array(locations[to_index]))
        return dist
        # return distance_matrix[from_index][to_index]

    problem_data = {
        'locations': locations,
        'demands': demands,
        'volumes': volumes,
        'time_windows': time_windows,
        'vehicle_capacities': vehicle_capacities,
        'distance_evaluator': distance_evaluator
    }

    return problem_data


def test_solver(solver, test_case):
    """
    Test a solver on a given test case.

    Args:
        solver: The solver to be tested
        test_case: The test case data

    Returns:
        The solution obtained by the solver
    """
    # Add logger to the kwargs
    test_case["logger"] = Logger()

    # Solve the VRP problem using the provided solver
    s = time()
    routes = solver(**test_case).solve()
    e = time()
    results = [
        {
            'total_time': route[-1]['arrival_time'],
            'total_volume': route[-1]['load'],
            'compute_time': e - s
        } for r, route in enumerate(routes)
    ]
    return results


def main():
    df = pd.DataFrame(columns=['num_locations', 'solver', 'total_time', 'total_volume', 'compute_time'])
    for num_locations in [10, 100, 1000, 10000]:
        for i in range(1):
            test_case = generate_test_case(
                num_locations=num_locations,
                num_vehicles=1,
                vehicle_capacity=num_locations*10,
                time_window_span=None
            )
            for solver in [AntColonySolver]:
                result = test_solver(solver, test_case)
                # print(result)
                df.loc[len(df)] = [
                    num_locations,
                    solver.__name__,
                    result[0]['total_time'],
                    result[0]['total_volume'],
                    result[0]['compute_time']
                ]
                print(df.loc[len(df)-1])
                df.to_csv('results.csv', index=False)

    print(df.head(20))
    print(df.info())
    print(df.describe())


if __name__ == "__main__":
    main()
