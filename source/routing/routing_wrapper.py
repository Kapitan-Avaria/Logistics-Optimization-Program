from source.routing.ors_routing_api_client import ORSRoutingClient
# from source.routing.yandex_routing_api_client import YandexRoutingClient
# from source.routing.yandex_in_browser_router import YandexInBrowserRouter
# from source.routing.yandex_in_browser_router_manual import YandexManualRoutingHelper

from source.config import Config
from time import sleep


class RoutingWrapper:

    def __init__(self):
        config = Config()
        self.clients = {
            'ors_api': ORSRoutingClient(config.ORS_ROUTING_API_KEY),
            # 'yandex_api': YandexRoutingClient(config.YANDEX_ROUTING_API_KEY),
            # 'yandex_selenium': YandexInBrowserRouter(),
            # 'yandex_manual': YandexManualRoutingHelper()
        }

    def get_distances(self, sources, destinations=None, time_sleep_seconds=1):
        res = self.clients['ors_api'].get_distances(sources, destinations)
        sleep(time_sleep_seconds)
        return res
