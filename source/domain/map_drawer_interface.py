from abc import ABC, abstractmethod


class MapDrawer(ABC):

    @abstractmethod
    def redraw_map(self):
        pass

    @abstractmethod
    def get_map_iframe(self):
        pass
