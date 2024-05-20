"""
Tests for solver
"""

from nsp_solver.utils import utils
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
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 0, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 1, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 2, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 0, 0), (0, 1, 3, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 0, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 1, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 2, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 1, 0), (0, 1, 3, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 0, 0)]},
            False,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 1, 0)]},
            False,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 2, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 2, 0), (0, 1, 3, 0)]},
            True,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 0, 0)]},
            False,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 1, 0)]},
            False,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 2, 0)]},
            False,
        ),
        (
            {"lastAssignedShiftType": "None", "schedule": [(0, 0, 3, 0), (0, 1, 3, 0)]},
            True,
        ),
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


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ({"skills": [], "schedule": [(0, 0, 3, 0)]}, False),
        (
            {
                "skills": ["HeadNurse", "Nurse", "Caretaker"],
                "schedule": [(0, 0, 3, 0), (0, 1, 3, 0)],
            },
            True,
        ),
        (
            {
                "skills": ["HeadNurse", "Nurse", "Caretaker"],
                "schedule": [(0, 0, 3, 0), (0, 1, 3, 1)],
            },
            True,
        ),
        (
            {
                "skills": ["HeadNurse", "Nurse", "Caretaker"],
                "schedule": [(0, 0, 3, 0), (0, 1, 3, 2)],
            },
            True,
        ),
        (
            {
                "skills": ["HeadNurse", "Nurse", "Caretaker"],
                "schedule": [(0, 0, 3, 0), (0, 1, 3, 3)],
            },
            False,
        ),
        ({"skills": ["Trainee"], "schedule": [(0, 0, 3, 0), (0, 1, 3, 3)]}, False),
        ({"skills": ["Trainee"], "schedule": [(0, 0, 3, 3), (0, 1, 3, 1)]}, False),
        ({"skills": ["Trainee"], "schedule": [(0, 0, 3, 3), (0, 1, 3, 2)]}, False),
        ({"skills": ["Trainee"], "schedule": [(0, 0, 3, 3), (0, 1, 3, 3)]}, True),
    ],
)
def test_is_required_skill_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["sc_data"]["nurses"][0]["skills"] = input_data["skills"]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_required_skill_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "numberOfConsecutiveWorkingDays": 3,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                ],
            },
            False,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "numberOfConsecutiveWorkingDays": 7,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                    (0, 5, 3, 0),
                    (0, 6, 3, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "numberOfConsecutiveWorkingDays": 1,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                    (0, 5, 3, 0),
                    (0, 6, 3, 0),
                ],
            },
            False,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                    (0, 5, 0, 0),
                    (0, 5, 3, 0),
                    (0, 6, 3, 0),
                ],
            },
            True,
        ),
    ],
)
def test_is_max_consecutive_work_days_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveWorkingDays"
    ] = input_data["numberOfConsecutiveWorkingDays"]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfConsecutiveWorkingDaysHard"] = input_data[
        "maximumNumberOfConsecutiveWorkingDaysHard"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_max_consecutive_work_days_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "numberOfConsecutiveWorkingDays": 1,
                "schedule": [],
            },
            False,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "numberOfConsecutiveWorkingDays": 2,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "numberOfConsecutiveWorkingDays": 1,
                "schedule": [
                    (0, 0, 3, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "numberOfConsecutiveWorkingDays": 1,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 4, 3, 0),
                    (0, 5, 0, 0),
                    (0, 5, 3, 0),
                    (0, 6, 3, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [
                    (0, 4, 3, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_min_consecutive_work_days_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveWorkingDays"
    ] = input_data["numberOfConsecutiveWorkingDays"]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["minimumNumberOfConsecutiveWorkingDaysHard"] = input_data[
        "minimumNumberOfConsecutiveWorkingDaysHard"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_min_consecutive_work_days_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "lastAssignedShiftType": "None",
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 5, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "numberOfConsecutiveAssignments": 5,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "numberOfConsecutiveAssignments": 5,
                "schedule": [(0, 0, 0, 0)],
            },
            False,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_max_consecutive_work_shifts_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "lastAssignedShiftType"
    ] = input_data["lastAssignedShiftType"]
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveAssignments"
    ] = input_data["numberOfConsecutiveAssignments"]
    constants_for_1_nurse["sc_data"]["shiftTypes"][0][
        "maximumNumberOfConsecutiveAssignmentsHard"
    ] = input_data["maximumNumberOfConsecutiveAssignmentsHard"]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_max_consecutive_work_shifts_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 5, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [(0, 0, 0, 0)],
            },
            True,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [],
            },
            False,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveAssignments": 2,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [(0, 0, 0, 0)],
            },
            False,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 6, 0, 0),
                ],
            },
            True,
        ),
    ],
)
def test_is_min_max_consecutive_assignments_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "lastAssignedShiftType"
    ] = input_data["lastAssignedShiftType"]
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveAssignments"
    ] = input_data["numberOfConsecutiveAssignments"]
    constants_for_1_nurse["sc_data"]["shiftTypes"][0][
        "minimumNumberOfConsecutiveAssignmentsHard"
    ] = input_data["minimumNumberOfConsecutiveAssignmentsHard"]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_min_consecutive_work_shifts_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
                "schedule": [
                    (0, 0, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveAssignments": 2,
                "lastAssignedShiftType": "Early",
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 1, 0),
                    (0, 5, 1, 0),
                    (0, 6, 1, 0),
                ],
            },
            False,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 5, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 1, 0),
                    (0, 2, 1, 0),
                    (0, 3, 1, 0),
                    (0, 4, 1, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_min_consecutive_work_shifts_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "lastAssignedShiftType"
    ] = input_data["lastAssignedShiftType"]
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveAssignments"
    ] = input_data["numberOfConsecutiveAssignments"]
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveWorkingDays"
    ] = input_data["numberOfConsecutiveWorkingDays"]
    constants_for_1_nurse["sc_data"]["shiftTypes"][0][
        "maximumNumberOfConsecutiveWorkingDaysHard"
    ] = input_data["maximumNumberOfConsecutiveWorkingDaysHard"]
    constants_for_1_nurse["sc_data"]["shiftTypes"][0][
        "minimumNumberOfConsecutiveWorkingDaysHard"
    ] = input_data["minimumNumberOfConsecutiveWorkingDaysHard"]
    constants_for_1_nurse["sc_data"]["shiftTypes"][0][
        "maximumNumberOfConsecutiveAssignmentsHard"
    ] = input_data["maximumNumberOfConsecutiveAssignmentsHard"]
    constants_for_1_nurse["sc_data"]["shiftTypes"][0][
        "minimumNumberOfConsecutiveAssignmentsHard"
    ] = input_data["minimumNumberOfConsecutiveAssignmentsHard"]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_min_max_consecutive_assignments_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfConsecutiveDaysOffHard": 4,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            True,
        ),
    ],
)
def test_is_max_consecutive_days_off_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week, capfd
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveDaysOff"
    ] = input_data["numberOfConsecutiveDaysOff"]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfConsecutiveDaysOffHard"] = input_data[
        "maximumNumberOfConsecutiveDaysOffHard"
    ]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_max_consecutive_days_off_satisfied()

    # Assert
    assert retval == expected
