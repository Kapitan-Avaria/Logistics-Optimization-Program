from abc import ABC, abstractmethod


class DeliveryPlannerInterface(ABC):
    @abstractmethod
    def request_data_from_api(self, api_url: str):
        pass

    @abstractmethod
    def load_data_from_db(self):
        pass
