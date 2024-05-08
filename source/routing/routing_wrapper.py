from ors_routing_api_client import ORSRoutingClient
from yandex_routing_api_client import YandexRoutingClient
from yandex_in_browser_router import YandexInBrowserRouter
from yandex_in_browser_router_manual import YandexManualRoutingHelper


class RoutingWrapper:

    def __init__(self):
        self.clients = {
            'ors-api': ORSRoutingClient(),
            'yandex-api': YandexRoutingClient(),
            'yandex-selenium': YandexInBrowserRouter(),
            'yandex-manual': YandexManualRoutingHelper()
        }
