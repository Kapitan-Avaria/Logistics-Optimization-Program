import openrouteservice
from openrouteservice.distance_matrix import distance_matrix


class ORSRoutingClient:

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = openrouteservice.Client(key=api_key)

    def get_distances(self, source, destinations):
        res = distance_matrix(
            self.client,
            locations=[source]+destinations,
            sources=[0],
            destinations=[i + 1 for i in range(len(destinations))]
        )
        return res["distances"]
