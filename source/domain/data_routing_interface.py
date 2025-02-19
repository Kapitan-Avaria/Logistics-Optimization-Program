from abc import ABC, abstractmethod


class RoutingDataInterface(ABC):
    @abstractmethod
    def get_segment_data(self, source: tuple[float, float], destination: tuple[float, float], segment_id) -> dict:
        pass
