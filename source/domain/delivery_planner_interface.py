from abc import ABC, abstractmethod
from source.domain.entities import Problem, Route


class DeliveryPlannerInterface(ABC):

    @abstractmethod
    def export_routes(self):
        pass

    @abstractmethod
    def build_routes(self, problem, solver):
        pass

    @abstractmethod
    def edit_route(self):
        pass
