from ors_routing_api_client import ORSRoutingClient
from yandex_routing_api_client import YandexRoutingClient
from yandex_in_browser_router import YandexInBrowserRouter
from yandex_in_browser_router_manual import YandexManualRoutingHelper

from source.constants import ORS_ROUTING_API_KEY, YANDEX_ROUTING_API_KEY


class RoutingWrapper:

    def __init__(self):
        self.clients = {
            'ors-api': ORSRoutingClient(ORS_ROUTING_API_KEY),
            'yandex-api': YandexRoutingClient(YANDEX_ROUTING_API_KEY),
            'yandex-selenium': YandexInBrowserRouter(),
            'yandex-manual': YandexManualRoutingHelper()
        }
