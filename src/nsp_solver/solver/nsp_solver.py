from abc import ABC, abstractmethod


class NSP_solver(ABC):
    """Abstract class that serves as the interface for solvers used for a compuation of a schedule for a week.
    """
    name: str

    @abstractmethod
    def compute_one_week(self, time_limit_for_week, data, results):
        """Computes a schedule for a week given a time limit and data.

        Args:
            time_limit_for_week (int): time limit for finding a schedule as optimal as possible
            data (dict): dictionary that contains data from input files
            results (dict): dictionary used to store partially computed schedule
        """
        pass
