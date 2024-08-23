from abc import ABC, abstractmethod


class NSP_solver(ABC):
    name: str

    @abstractmethod
    def compute_one_week(self, time_limit_for_week, constants, results):
        pass
