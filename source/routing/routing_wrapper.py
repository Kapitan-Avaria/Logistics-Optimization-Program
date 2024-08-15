from source.routing.ors_routing_api_client import ORSRoutingClient
from source.routing.yandex_routing_api_client import YandexRoutingClient
from source.routing.yandex_in_browser_router import YandexInBrowserRouter
from source.routing.yandex_in_browser_router_manual import YandexManualRoutingHelper

from source.config import Config


class RoutingWrapper:

    def __init__(self):
        config = Config()
        self.clients = {
            'ors-api': ORSRoutingClient(config.ORS_ROUTING_API_KEY),
            'yandex-api': YandexRoutingClient(config.YANDEX_ROUTING_API_KEY),
            'yandex-selenium': YandexInBrowserRouter(),
            'yandex-manual': YandexManualRoutingHelper()
        }

    def get_distances(self, sources, destinations=None):
        res = self.clients['ors-api'].get_distances(sources, destinations)
