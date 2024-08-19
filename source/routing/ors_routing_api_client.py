import openrouteservice
from openrouteservice.distance_matrix import distance_matrix


class ORSRoutingClient:

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = openrouteservice.Client(key=api_key)

    def get_distances(self, sources, destinations=None):
        sources = [list(map(str, s)) for s in sources]
        if destinations is None:
            res = distance_matrix(
                self.client,
                locations=sources,
                metrics=["distance", "duration"]
            )
        else:
            destinations = [list(map(str, d)) for d in destinations]
            res = distance_matrix(
                self.client,
                locations=sources+destinations,
                sources=[i for i in range(len(sources))],
                destinations=[i + len(sources) for i in range(len(destinations))],
                metrics=["distance", "duration"]
            )
        return res["distances"], res["durations"]
