from abc import ABC, abstractmethod


class GeoDataInterface(ABC):
    @abstractmethod
    def geocode(self, address_string) -> tuple[float, float]:
        pass

    @abstractmethod
    def geocode_reverse(self, lat: float, lon: float) -> str:
        pass
