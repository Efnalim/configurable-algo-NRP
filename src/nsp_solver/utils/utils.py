from enum import Enum
from contextlib import contextmanager
import sys

shift_to_int = {"Early": 0, "Day": 1, "Late": 2, "Night": 3, "Any": 4, "None": 5}
skill_to_int = {"HeadNurse": 0, "Nurse": 1, "Caretaker": 2, "Trainee": 3}
contract_to_int = {"FullTime": 0, "PartTime": 1, "HalfTime": 2}
day_to_int = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
OPT_CAPACITY_WEIGHT = 30
CONS_WORK_DAY_WEIGHT = 30
CONS_SHIFT_WEIGHT = 15
CONS_DAY_OFF_WEIGHT = 30
UNSATISFIED_PREFERENCE_WEIGHT = 10
INCOMPLETE_WEEKEDN_WEIGHT = 30
CONS_WORK_DAY_WEIGHT = 30
TOTAL_ASSIGNMENTS_WEIGHT = 20
TOTAL_WORKING_WEEKENDS_WEIGHT = 30
TOTAL_IFNEEDED_SKILL_WEIGHT = 15
UNSATISFIED_OVERTIME_PREFERENCE_WEIGHT = 10

STATUS_OK = 'solution found'
STATUS_FAIL = 'solution not found'


def isPositiveNumber(number):
    """_summary_

    Args:
        number (_type_): _description_

    Returns:
        _type_: _description_
    """
    if number > 0:
        return 1
    return 0


def soft_constr_value_print(func):
    """_summary_

    Args:
        func (_type_): _description_
    """
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.soft_table.append([func.__name__, result])
        # print(f"Function {func.__name__} returned: {result}")
        return result
    return wrapper


def hard_constr_value_print(func):
    """_summary_

    Args:
        func (_type_): _description_
    """
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.hard_table.append([func.__name__, result])
        # print(f"Function {func.__name__} returned: {result}")
        return result
    return wrapper


def print_table(name, table):
    """_summary_

    Args:
        name (_type_): _description_
        table (_type_): _description_
    """
    print(name)

    col_widths = [max(len(str(item)) for item in column) for column in zip(*table)]
    print("+" * (sum(col_widths) + len(col_widths) + 1))
    for index, row in enumerate(table):
        print(" | ".join(str(item).ljust(width) for item, width in zip(row, col_widths)))
        if index == 0:
            print("-" * (sum(col_widths) + len(col_widths) + 1))
    print()


class Shift_placement(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_
    """
    START = 0
    MID = 1
    END = 2


@contextmanager
def redirect_stdout_to_file(file_path):
    """_summary_

    Args:
        file_path (_type_): _description_
    """
    original_stdout = sys.stdout
    with open(file_path, 'w') as file:
        sys.stdout = file
        yield
    sys.stdout = original_stdout
