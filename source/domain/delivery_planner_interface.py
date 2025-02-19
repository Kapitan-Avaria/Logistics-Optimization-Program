from abc import ABC, abstractmethod


class DeliveryPlannerInterface(ABC):
    # @abstractmethod
    # def request_data_from_api(self, api_url: str):
    #     pass

    @abstractmethod
    def export_routes(self):
        pass

    @abstractmethod
    def build_routes(self):
        pass

    @abstractmethod
    def edit_route(self):
        pass
