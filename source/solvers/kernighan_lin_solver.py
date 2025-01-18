import random
import math
from itertools import combinations, permutations, product

class KernighanLinSolver:
    def __init__(self, locations, demands, vehicle_capacity, initial_route=None, distance_evaluator=None):
        self.locations = locations
        self.demands = demands
        self.vehicle_capacity = vehicle_capacity
        self.initial_route = initial_route
        self.distance_evaluator = distance_evaluator if distance_evaluator else self.default_distance_evaluator
        self.distance_matrix = self.calculate_distance_matrix()

    def default_distance_evaluator(self, loc1, loc2):
        """
        Default distance evaluator using Euclidean distance.
        """
        return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)

    def calculate_distance_matrix(self):
        """
        Calculate the distance matrix for all locations.
        """
        size = len(self.locations)
        distance_matrix = [[0] * size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                distance_matrix[i][j] = self.distance_evaluator(self.locations[i], self.locations[j])
        return distance_matrix

    def calculate_distance(self, route):
        """
        Calculate the total distance of the given route using the distance matrix.
        """
        total_distance = 0
        for i in range(len(route)):
            total_distance += self.distance_matrix[route[i]][route[(i + 1) % len(route)]]
        return total_distance

    def k_opt(self, route, k):
        """
        Perform a k-opt optimization on the given route.
        """
        best_route = route[:]
        best_distance = self.calculate_distance(best_route)
        improved = True

        while improved:
            improved = False
            # Generate all combinations of k edges to consider for replacement
            for edges_to_replace in combinations(range(len(route)), k):
                # Generate all possible rearrangements of these edges
                new_routes = self.generate_k_opt_variants(route, edges_to_replace)

                for new_route in new_routes:
                    new_distance = self.calculate_distance(new_route)
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True

            route = best_route

        return best_route, best_distance

    def generate_k_opt_variants(self, route, edges_to_replace):
        """
        Generate all possible k-opt variants by rearranging the given edges.
        """
        new_routes = []
        n = len(route)

        # Break the route into segments defined by edges_to_replace
        segments = []
        prev = 0
        for edge in sorted(edges_to_replace):
            segments.append(route[prev:edge + 1])
            prev = edge + 1
        segments.append(route[prev:] + route[:segments[0][0]])  # Complete the cycle

        # Generate permutations of the segments
        segment_permutations = permutations(segments)

        for perm in segment_permutations:
            # Reverse segments if needed and reconstruct the route
            for reversed_segments in product([True, False], repeat=len(segments)):
                new_route = []
                for segment, reverse in zip(perm, reversed_segments):
                    new_route.extend(segment[::-1] if reverse else segment)
                # Ensure it forms a valid cycle
                if len(set(new_route)) == n:
                    new_routes.append(new_route[:n])

        return new_routes

    def solve(self):
        """
        Solve the TSP using an adaptation of the Kernighan-Lin algorithm with dynamic k-opt optimization.
        """
        num_nodes = len(self.distance_matrix)
        # Use the initial route if provided, otherwise generate a random one
        route = self.initial_route[0] if self.initial_route else list(range(num_nodes))
        if not self.initial_route:
            random.shuffle(route)

        best_route = route[:]
        best_distance = self.calculate_distance(route)

        k = 2  # Start with 2-opt

        for iteration in range(100):  # Limit the number of iterations
            # Split the route into two groups
            split_point = random.randint(1, num_nodes - 1)
            group_a = route[:split_point]
            group_b = route[split_point:]

            # Perform swaps between the groups to minimize the total distance
            for _ in range(10):  # Limit the number of swaps
                best_swap = None
                best_improvement = 0

                for i in range(len(group_a)):
                    for j in range(len(group_b)):
                        new_group_a = group_a[:i] + [group_b[j]] + group_a[i + 1:]
                        new_group_b = group_b[:j] + [group_a[i]] + group_b[j + 1:]

                        new_route = new_group_a + new_group_b
                        new_distance = self.calculate_distance(new_route)
                        improvement = best_distance - new_distance

                        if improvement > best_improvement:
                            best_swap = (i, j)
                            best_improvement = improvement

                if best_swap is None:
                    break

                # Apply the best swap
                i, j = best_swap
                group_a[i], group_b[j] = group_b[j], group_a[i]

            # Recombine the groups and apply k-opt optimization
            route = group_a + group_b
            route, distance = self.k_opt(route, k)

            if distance < best_distance:
                best_route = route[:]
                best_distance = distance
                k = min(k + 1, num_nodes - 1)  # Dynamically increase k
            else:
                k = max(2, k - 1)  # Dynamically decrease k

        return best_route, best_distance

# Example usage
locations = [(0, 0), (1, 1), (2, 2), (3, 3)]
demands = [0, 0, 0, 0]
vehicle_capacity = 10
solver = KernighanLinSolver(locations, demands, vehicle_capacity)

best_route, best_distance = solver.solve()
print("Best route:", best_route)
print("Best distance:", best_distance)
