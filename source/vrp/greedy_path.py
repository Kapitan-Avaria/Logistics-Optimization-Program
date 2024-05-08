
def greedy_path(addresses_ids, capacity):
    node_address_map = {node_index: address_id for node_index, address_id in enumerate(addresses_ids)}

    nodes = [i for i in range(1, len(node_address_map.keys())+1)]
    path = [0]
    cur_point = 0

    total_travel_time = 0
    total_volume = 0

    while len(nodes) > 0:
        min_distance = 1e7
        target = -1

        for point in nodes:
            travel_time = calc_travel_time(node_address_map[cur_point], node_address_map[point])
            if travel_time <= min_distance:
                min_distance = travel_time
                target = point

        path.append(target)
        nodes.remove(target)
        cur_point = target
        total_travel_time += travel_time


def calc_travel_time(address_id_1, address_id_2) -> float:
    pass
