import numpy as np

from source.domain.database_interface import DatabaseInterface


def create_distance_evaluator_from_data(addresses: list, db: DatabaseInterface):
    def distance_evaluator(from_node, to_node):
        nonlocal addresses
        if addresses[from_node] == addresses[to_node]:
            return 0.
        distance = db.get_segment_statistics(db.get_segment(
            addresses[from_node].id,
            addresses[to_node].id
        ).id)[0].distance
        return distance

    return distance_evaluator


def create_euclidian_distance_evaluator(locations: list):

    def distance_evaluator(from_index, to_index):
        nonlocal locations
        dist = np.linalg.norm(np.array(locations[from_index]) - np.array(locations[to_index]))
        return dist

    return distance_evaluator
