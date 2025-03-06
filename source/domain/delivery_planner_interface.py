from abc import ABC, abstractmethod
from source.domain.entities import Problem, Route


class DeliveryPlannerInterface(ABC):
    def __init__(self):
        self.problem: Problem = None

    @abstractmethod
    def export_routes(self):
        pass

    @abstractmethod
    def build_routes(self):
        pass

    @abstractmethod
    def edit_route(self):
        pass
