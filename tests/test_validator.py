"""
Tests for solver
"""

import numpy as np
import pytest

from src.nsp_solver.validator.validator import ScheduleValidator


def test_compute_helpful_values__1nurse_5shifts_5_days(validator_for_1nurse_1week):
    """This is a mock test"""
    # Arrange
    validator = validator_for_1nurse_1week
    results = validator.schedule
    results[(0, 0, 0, 0)] = 1
    results[(0, 1, 1, 1)] = 1
    results[(0, 2, 2, 2)] = 1
    results[(0, 3, 1, 1)] = 1
    results[(0, 4, 0, 0)] = 1

    # Execute
    help_vars = validator.compute_helpful_values()

    # Assert
    assert help_vars["working_days"][0][0] == 1
    assert help_vars["working_days"][0][1] == 1
    assert help_vars["working_days"][0][2] == 1
    assert help_vars["working_days"][0][3] == 1
    assert help_vars["working_days"][0][4] == 1
    assert np.sum(np.array(help_vars["working_days"])) == 5

    assert help_vars["shifts"][0][0][0] == 1
    assert help_vars["shifts"][0][1][1] == 1
    assert help_vars["shifts"][0][2][2] == 1
    assert help_vars["shifts"][0][3][1] == 1
    assert help_vars["shifts"][0][4][0] == 1
    assert np.sum(np.array(help_vars["shifts"])) == 5


def test_compute_helpful_values__1nurse_5_4_days(validator_for_1nurse_1week):
    """This is a mock test"""
    # Arrange
    validator = validator_for_1nurse_1week
    results = validator.schedule
    results[(0, 0, 0, 0)] = 1
    results[(0, 0, 3, 0)] = 1
    results[(0, 1, 1, 1)] = 1
    results[(0, 2, 2, 2)] = 1
    results[(0, 3, 1, 1)] = 1

    # Execute
    help_vars = validator.compute_helpful_values()

    # Assert
    assert help_vars["working_days"][0][0] == 1
    assert help_vars["working_days"][0][1] == 1
    assert help_vars["working_days"][0][2] == 1
    assert help_vars["working_days"][0][3] == 1
    assert np.sum(np.array(help_vars["working_days"])) == 4

    assert help_vars["shifts"][0][0][0] == 1
    assert help_vars["shifts"][0][0][3] == 1
    assert help_vars["shifts"][0][1][1] == 1
    assert help_vars["shifts"][0][2][2] == 1
    assert help_vars["shifts"][0][3][1] == 1
    assert np.sum(np.array(help_vars["shifts"])) == 5


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ([], True),
        ([(0, 0, 3, 0), (0, 1, 3, 0), (0, 2, 3, 0), (0, 3, 3, 0), (0, 4, 3, 0)], True),
        ([(0, 5, 0, 0), (0, 6, 0, 0), (0, 6, 3, 0)], False),
    ],
)
def test_is_max_assignments_per_day_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data:
        schedule[input] = 1
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_max_assignments_per_day_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ({"lastAssignedShiftType": "None", "schedule": []}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0)]}, True),
        ({"lastAssignedShiftType": "Early", "schedule": []}, True),
        ({"lastAssignedShiftType": "Early", "schedule": [(0, 0, 0, 0)]}, True),
        ({"lastAssignedShiftType": "Early", "schedule": [(0, 0, 1, 0)]}, True),
        ({"lastAssignedShiftType": "Early", "schedule": [(0, 0, 2, 0)]}, True),
        ({"lastAssignedShiftType": "Early", "schedule": [(0, 0, 3, 0)]}, True),
        ({"lastAssignedShiftType": "Day", "schedule": []}, True),
        ({"lastAssignedShiftType": "Day", "schedule": [(0, 0, 0, 0)]}, True),
        ({"lastAssignedShiftType": "Day", "schedule": [(0, 0, 1, 0)]}, True),
        ({"lastAssignedShiftType": "Day", "schedule": [(0, 0, 2, 0)]}, True),
        ({"lastAssignedShiftType": "Day", "schedule": [(0, 0, 3, 0)]}, True),
        ({"lastAssignedShiftType": "Late", "schedule": []}, True),
        ({"lastAssignedShiftType": "Late", "schedule": [(0, 0, 0, 0)]}, False),
        ({"lastAssignedShiftType": "Late", "schedule": [(0, 0, 1, 0)]}, False),
        ({"lastAssignedShiftType": "Late", "schedule": [(0, 0, 2, 0)]}, True),
        ({"lastAssignedShiftType": "Late", "schedule": [(0, 0, 3, 0)]}, True),
        ({"lastAssignedShiftType": "Night", "schedule": []}, True),
        ({"lastAssignedShiftType": "Night", "schedule": [(0, 0, 0, 0)]}, False),
        ({"lastAssignedShiftType": "Night", "schedule": [(0, 0, 1, 0)]}, False),
        ({"lastAssignedShiftType": "Night", "schedule": [(0, 0, 2, 0)]}, False),
        ({"lastAssignedShiftType": "Night", "schedule": [(0, 0, 3, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": []}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 0, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 1, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 2, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 3, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 0, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 1, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 2, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 3, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 0, 0)]}, False),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 1, 0)]}, False),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 2, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 3, 0)]}, True),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 0, 0)]}, False),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 1, 0)]}, False),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 2, 0)]}, False),
        ({"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 3, 0)]}, True),
    ],
)
def test_is_shift_successsion_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "lastAssignedShiftType"
    ] = input_data["lastAssignedShiftType"]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_shift_successsion_satisfied()

    # Assert
    assert retval == expected
