#!/usr/bin/env python3
# Copyright 2010-2024 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START program]
"""Capacitated Vehicle Routing Problem with Time Windows (CVRPTW).

   This is a sample using the routing library python wrapper to solve a CVRPTW
   problem.
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.

   Distances are in meters and time in minutes.
"""

# [START import]
import functools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
# [END import]


# [START data_model]
def create_data_model(demands: list, distances: dict, times, vehicles_capacities: list):
    """Stores the data for the problem."""
    data = dict()

    data["numlocations_"] = len(demands)
    data["distances"] = distances
    data["times"] = times
    data["time_windows"] = [(0, 0)] + [(8 * 60, 18 * 60)] * (data["numlocations_"] - 1)
    data["demands"] = demands
    data["time_per_demand_unit"] = 5  # 5 minutes/unit
    data["num_vehicles"] = len(vehicles_capacities)
    data["vehicle_capacities"] = vehicles_capacities
    data["vehicle_speed"] = 600  # m/min (36 km/h)
    data["depot"] = 0
    return data
# [END data_model]


def create_distance_evaluator(data):
    """Creates callback to return distance between points."""
    distances_ = {}
    # precompute distance between location to have distance callback in O(1)
    for from_node in range(data["numlocations_"]):
        distances_[from_node] = {}
        for to_node in range(data["numlocations_"]):
            if from_node == to_node:
                distances_[from_node][to_node] = 0
            else:
                distances_[from_node][to_node] = data["distances"][(from_node, to_node)]

    def distance_evaluator(manager, from_node, to_node):
        """Returns the manhattan distance between the two nodes."""
        return distances_[manager.IndexToNode(from_node)][manager.IndexToNode(to_node)]

    return distance_evaluator


def create_demand_evaluator(data):
    """Creates callback to get demands at each location."""
    demands_ = data["demands"]

    def demand_evaluator(manager, node):
        """Returns the demand of the current node."""
        return demands_[manager.IndexToNode(node)]

    return demand_evaluator


def add_capacity_constraints(routing, data, demand_evaluator_index):
    """Adds capacity constraint."""
    capacity = "Capacity"
    routing.AddDimensionWithVehicleCapacity(
        demand_evaluator_index,
        0,  # null capacity slack
        data["vehicle_capacities"],
        True,  # start cumul to zero
        capacity,
    )


def create_time_evaluator(data):
    """Creates callback to get total times between locations."""

    def service_time(data, node):
        """Gets the service time for the specified location."""
        return data["demands"][node] * data["time_per_demand_unit"]

    def travel_time(data, from_node, to_node):
        """Gets the travel times between two locations."""
        if from_node == to_node:
            travel_time_ = 0
        else:
            travel_time_ = data["times"][(from_node, to_node)]
        return travel_time_

    total_time_ = {}
    # precompute total time to have time callback in O(1)
    for from_node in range(data["numlocations_"]):
        total_time_[from_node] = {}
        for to_node in range(data["numlocations_"]):
            if from_node == to_node:
                total_time_[from_node][to_node] = 0
            else:
                total_time_[from_node][to_node] = int(
                    service_time(data, from_node)
                    + travel_time(data, from_node, to_node)
                )

    def time_evaluator(manager, from_node, to_node):
        """Returns the total time between the two nodes."""
        return total_time_[manager.IndexToNode(from_node)][manager.IndexToNode(to_node)]

    return time_evaluator


def add_time_window_constraints(routing, manager, data, time_evaluator_index):
    """Add Global Span constraint."""
    time = "Time"
    horizon = 400
    routing.AddDimension(
        time_evaluator_index,
        horizon,  # allow waiting time
        horizon,  # maximum time per vehicle
        False,  # don't force start cumul to zero
        time,
    )
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot
    # and 'copy' the slack var in the solution object (aka Assignment) to print it
    for location_idx, time_window in enumerate(data["time_windows"]):
        if location_idx == data["depot"]:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        routing.AddToAssignment(time_dimension.SlackVar(index))
    # Add time window constraints for each vehicle start node
    # and 'copy' the slack var in the solution object (aka Assignment) to print it
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][0][0], data["time_windows"][0][1]
        )
        routing.AddToAssignment(time_dimension.SlackVar(index))
        # The time window at the end node was impliclty set in the time dimension
        # definition to be [0, horizon].
        # Warning: Slack var is not defined for vehicle end nodes and should not
        # be added to the assignment.
        

# [START solution_printer]
def print_solution(
    data, manager, routing, assignment
):  # pylint:disable=too-many-locals
    """Prints assignment on console."""
    print(f"Objective: {assignment.ObjectiveValue()}")

    total_distance = 0
    total_load = 0
    total_time = 0
    capacity_dimension = routing.GetDimensionOrDie("Capacity")
    time_dimension = routing.GetDimensionOrDie("Time")
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        distance = 0
        while not routing.IsEnd(index):
            load_var = capacity_dimension.CumulVar(index)
            time_var = time_dimension.CumulVar(index)
            slack_var = time_dimension.SlackVar(index)
            node = manager.IndexToNode(index)
            plan_output += (
                f" {node}"
                f" Load({assignment.Value(load_var)})"
                f" Time({assignment.Min(time_var)}, {assignment.Max(time_var)})"
                f" Slack({assignment.Min(slack_var)}, {assignment.Max(slack_var)})"
                " ->"
            )
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        load_var = capacity_dimension.CumulVar(index)
        time_var = time_dimension.CumulVar(index)
        node = manager.IndexToNode(index)
        plan_output += (
            f" {node}"
            f" Load({assignment.Value(load_var)})"
            f" Time({assignment.Min(time_var)}, {assignment.Max(time_var)})\n"
        )
        plan_output += f"Distance of the route: {distance}m\n"
        plan_output += f"Load of the route: {assignment.Value(load_var)}\n"
        plan_output += f"Time of the route: {assignment.Value(time_var)}\n"
        print(plan_output)
        total_distance += distance
        total_load += assignment.Value(load_var)
        total_time += assignment.Value(time_var)
    print(f"Total Distance of all routes: {total_distance}m")
    print(f"Total Load of all routes: {total_load}")
    print(f"Total Time of all routes: {total_time}min")
# [END solution_printer]


def save_solution_to_dict(data, manager, routing, assignment):
    """Saves assignment to dict."""
    solution = dict()
    solution["objective"] = assignment.ObjectiveValue()
    solution["routes"] = []

    total_distance = 0
    total_load = 0
    total_time = 0
    capacity_dimension = routing.GetDimensionOrDie("Capacity")
    time_dimension = routing.GetDimensionOrDie("Time")
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        route = dict()
        route["vehicle_id"] = vehicle_id
        route["path"] = []
        distance = 0
        while not routing.IsEnd(index):
            load_var = capacity_dimension.CumulVar(index)
            time_var = time_dimension.CumulVar(index)
            slack_var = time_dimension.SlackVar(index)
            node = manager.IndexToNode(index)

            route["path"].append({
                "node":  node,
                "delivered": assignment.Value(load_var),
                "time": (assignment.Min(time_var), assignment.Max(time_var)),
                "slack": (assignment.Min(slack_var), assignment.Max(slack_var))
            })

            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        load_var = capacity_dimension.CumulVar(index)
        time_var = time_dimension.CumulVar(index)
        node = manager.IndexToNode(index)
        route["path"].append({
            "node":  node,
            "delivered": assignment.Value(load_var),
            "time": (assignment.Min(time_var), assignment.Max(time_var)),
        })
        route["distance"] = distance
        route["load"] = assignment.Value(load_var)
        route["time"] = assignment.Value(time_var)
        solution["routes"].append(route)

        total_distance += distance
        total_load += assignment.Value(load_var)
        total_time += assignment.Value(time_var)

    solution["total_distance"] = total_distance
    solution["total_load"] = total_load
    solution["total_time"] = total_time
    return solution


def solve(data):
    """Entry point of the program."""

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        data["numlocations_"], data["num_vehicles"], data["depot"]
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Define weight of each edge
    distance_evaluator_index = routing.RegisterTransitCallback(
        functools.partial(create_distance_evaluator(data), manager)
    )
    routing.SetArcCostEvaluatorOfAllVehicles(distance_evaluator_index)

    # Add Capacity constraint
    demand_evaluator_index = routing.RegisterUnaryTransitCallback(
        functools.partial(create_demand_evaluator(data), manager)
    )
    add_capacity_constraints(routing, data, demand_evaluator_index)

    # Add Time Window constraint
    time_evaluator_index = routing.RegisterTransitCallback(
        functools.partial(create_time_evaluator(data), manager)
    )
    add_time_window_constraints(routing, manager, data, time_evaluator_index)

    # Setting first solution heuristic (cheapest addition).
    # [START parameters]
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )  # pylint: disable=no-member
    # [END parameters]

    # Solve the problem.
    # [START solve]
    assignment = routing.SolveWithParameters(search_parameters)
    # [END solve]

    # Print solution on console.
    # [START print_solution]
    if assignment:
        print_solution(data, manager, routing, assignment)
        return save_solution_to_dict(data, manager, routing, assignment)
    else:
        print("No solution found!")
    # [END print_solution]


# if __name__ == "__main__":
#     Instantiate the data problem.
#     [START data]
#     data = create_data_model(nodes, demands, distances)
#     [END data]
#     run(data)

# [END program]
