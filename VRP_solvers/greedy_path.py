
def greedy_path():
    nodes = [i for i in range(1, n+1)]
    path = [0]
    cur_point = 0
    total_travel_time = 0
    while len(nodes) > 0:
        min_distance = 1e7
        for point in nodes:
            travel_time = calc_travel_time(cur_point, point)
            if travel_time <= min_distance:
                min_distance = travel_time
                target = point
        path.append(target)
        nodes.remove(target)
        cur_point = target
        total_travel_time += travel_time


