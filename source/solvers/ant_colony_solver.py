import numpy as np
import random
from source.domain.vrp_solver_interface import VRPSolverInterface


# --- Основные параметры ---
class AntColonySolver(VRPSolverInterface):
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
            logger=None,
            num_ants=10,
            num_iterations=5,
            alpha=1.0,
            beta=2.0,
            evaporation_rate=0.1,
            Q=100
    ):
        super().__init__(locations, demands, volumes, time_windows, vehicle_capacities, vehicle_time_windows, starts,
                         ends, distance_evaluator, logger)
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha  # Влияние феромона
        self.beta = beta  # Влияние эвристики
        self.evaporation_rate = evaporation_rate
        self.Q = Q  # Константа феромона
        self.num_nodes = len(locations)
        self.pheromone = np.ones((self.num_nodes, self.num_nodes))  # Матрица феромонов
        self.best_cost = float('inf')
        self.best_solution = None

    def initial_solution(self):
        return [[0] for _ in range(self.num_ants)]

    def calculate_probabilities(self, current_node, unvisited):
        total_pheromone = 0
        probabilities = []

        for next_node in unvisited:
            pheromone_level = self.pheromone[current_node][next_node]
            distance = float(self.distance_evaluator(current_node, next_node) / 1000)
            attractiveness = pheromone_level ** self.alpha * (1.0 / distance) ** self.beta
            probabilities.append(attractiveness)
            total_pheromone += attractiveness

        probabilities = [p / total_pheromone for p in probabilities]
        return probabilities

    def construct_solution(self):
        solutions = []
        vehicle_loads = [0] * self.vehicle_count
        vehicle_times = [0] * self.vehicle_count

        for ant in range(self.num_ants):
            route = [{
                "loc": 0,
                "arrival_time": 0.0,
                "wait_time": 0.0,
                "load": 0.0
            }]
            # current_load = 0
            self.unvisited = set(range(1, self.num_nodes))

            while self.unvisited:
                current_node = route[-1]['loc']
                feasible_nodes = self.select_feasible_locations(vehicle_loads, 0)

                if not feasible_nodes:
                    break
                    route.append(0)  # Вернуться в депо
                    # current_load = 0
                else:
                    current_time = vehicle_times[0]
                    vehicle_load = vehicle_loads[0]
                    probabilities = self.calculate_probabilities(current_node, feasible_nodes)
                    next_node = random.choices(feasible_nodes, weights=probabilities)[0]
                    new_time, new_load, wait_time, success = self.try_add_to_route(
                        route, next_node, current_time, vehicle_load, self.vehicle_capacities[0]
                    )
                    if success:
                        route.append(
                            {
                                "loc": next_node,
                                "arrival_time": new_time,
                                "wait_time": wait_time,
                                "load": new_load
                            }
                        )
                        vehicle_times[0] = new_time
                        vehicle_loads[0] = new_load
                        self.unvisited.remove(next_node)

                    # route.append(next_node)
                    # current_load += self.demands[next_node]

            # route.append(0)  # Вернуться в депо
            solutions.append(route)

        return solutions

    def calculate_cost(self, solution):
        total_cost = 0

        for route in solution:
            for i in range(len(route) - 1):
                total_cost += self.distance_evaluator(route[i]['loc'], route[i + 1]['loc'])

        return total_cost

    def update_pheromones(self, solutions, costs):
        self.pheromone *= (1 - self.evaporation_rate)  # Испарение феромонов

        for solution, cost in zip(solutions, costs):
            for route in solution:
                for i in range(len(route) - 1):
                    self.pheromone[route[i]['loc'], route[i + 1]['loc']] += self.Q / cost

    def solve(self):
        for iteration in range(self.num_iterations):
            solutions = [self.construct_solution() for _ in range(self.num_ants)]
            costs = [self.calculate_cost(solution) for solution in solutions]

            best_iteration_cost = min(costs)
            best_iteration_solution = solutions[costs.index(best_iteration_cost)]

            if best_iteration_cost < self.best_cost:
                self.best_cost = best_iteration_cost
                self.best_solution = best_iteration_solution

            self.update_pheromones(solutions, costs)

            self.lg.print(f"Iteration {iteration + 1}, Best Cost: {self.best_cost}")

        return self.best_solution  # , self.best_cost


if __name__ == '__main__':
    # --- Пример использования ---
    demands = [0, 10, 15, 10, 20, 25]  # Потребности клиентов (0 - депо)
    capacity = 50  # Вместимость транспортного средства

    distance_matrix = [
        [0, 2, 9, 10, 7, 12],
        [2, 0, 6, 4, 3, 8],
        [9, 6, 0, 7, 4, 2],
        [10, 4, 7, 0, 3, 5],
        [7, 3, 4, 3, 0, 6],
        [12, 8, 2, 5, 6, 0]
    ]

    aco_vrp = AntColonySolver(
        num_ants=10,
        num_iterations=50,
        alpha=1.0,
        beta=2.0,
        evaporation_rate=0.1,
        Q=100,
        demands=demands,
    )

    best_solution, best_cost = aco_vrp.solve()
    print("Best Solution:", best_solution)
    print("Best Cost:", best_cost)
