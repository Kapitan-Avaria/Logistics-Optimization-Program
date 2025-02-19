from source.domain.delivery_planner_interface import DeliveryPlannerInterface
from source.domain.data_operator import DataOperator
from source.domain.entities import *


class DeliveryPlanner(DeliveryPlannerInterface):

    def __init__(self):
        self.problem: Problem = None

    def set_problem(self, problem: Problem):
        self.problem = problem

    def export_routes(self):
        pass

    def build_routes(self):
        pass

    def edit_route(self):
        pass
