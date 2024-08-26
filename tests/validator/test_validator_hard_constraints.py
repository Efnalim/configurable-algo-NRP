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
    help_vars = validator._compute_helpful_values()

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
    help_vars = validator._compute_helpful_values()

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
    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_max_assignments_per_day_satisfied()

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
def _test_is_shift_successsion_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "lastAssignedShiftType"
    ] = input_data["lastAssignedShiftType"]
    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_shift_successsion_satisfied()

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
def _test_is_required_skill_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["sc_data"]["nurses"][0]["skills"] = input_data["skills"]
    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_required_skill_satisfied()

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
def _test_is_max_consecutive_work_days_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
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
    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_max_consecutive_work_days_satisfied()

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
def _test_is_min_consecutive_work_days_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
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
    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_min_consecutive_work_days_satisfied()

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
def _test_is_max_consecutive_work_shifts_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
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

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_max_consecutive_work_shifts_satisfied()

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
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
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

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_min_consecutive_work_shifts_satisfied()

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
def _test_is_min_consecutive_work_shifts_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
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

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_min_max_consecutive_assignments_satisfied()

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
                    (0, 4, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOffHard": 4,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": [
                    (0, 3, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOffHard": 4,
                "numberOfConsecutiveDaysOff": 4,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOffHard": 4,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": [
                    (0, 5, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOffHard": 4,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": [
                    (0, 4, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOffHard": 4,
                "numberOfConsecutiveDaysOff": 4,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_max_consecutive_days_off_satisfied(
    input_data, expected, constants_for_1_nurse, empty_results_1nurse_1week
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

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_max_consecutive_days_off_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "numberOfConsecutiveDaysOff": 4,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "numberOfConsecutiveDaysOff": 4,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 5, 0, 0),
                ],
            },
            True,
        ),
    ],
)
def test_is_min_consecutive_days_off_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
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
    ]["minimumNumberOfConsecutiveDaysOffHard"] = input_data[
        "minimumNumberOfConsecutiveDaysOffHard"
    ]

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_min_consecutive_days_off_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfIncompleteWeekendsHard": 0,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "maximumNumberOfIncompleteWeekendsHard": 0,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfIncompleteWeekendsHard": 0,
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
                "maximumNumberOfIncompleteWeekendsHard": 0,
                "schedule": [
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "maximumNumberOfIncompleteWeekendsHard": 0,
                "schedule": [
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
                "maximumNumberOfIncompleteWeekendsHard": 0,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_max_total_incomplete_weekends_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfIncompleteWeekendsHard"] = input_data[
        "maximumNumberOfIncompleteWeekendsHard"
    ]

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_max_total_incomplete_weekends_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimumNumberOfAssignmentsHard": 3,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimumNumberOfAssignmentsHard": 3,
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
                "minimumNumberOfAssignmentsHard": 3,
                "schedule": [],
            },
            False,
        ),
        (
            {
                "minimumNumberOfAssignmentsHard": 3,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_min_total_assignments_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["minimumNumberOfAssignmentsHard"] = input_data["minimumNumberOfAssignmentsHard"]

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_min_total_assignments_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfAssignmentsHard": 5,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "maximumNumberOfAssignmentsHard": 5,
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
                "maximumNumberOfAssignmentsHard": 5,
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
                "maximumNumberOfAssignmentsHard": 5,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_max_total_assignments_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfAssignmentsHard"] = input_data["maximumNumberOfAssignmentsHard"]

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_max_total_assignments_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimalFreePeriod": 2,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": [],
            },
            True,
        ),
        (
            {
                "minimalFreePeriod": 2,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimalFreePeriod": 2,
                "numberOfConsecutiveDaysOff": 4,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "minimalFreePeriod": 2,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "minimalFreePeriod": 2,
                "numberOfConsecutiveDaysOff": 4,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_min_free_period_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
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
    ]["minimalFreePeriod"] = input_data["minimalFreePeriod"]

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_min_free_period_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "schedule": [],
            },
            True,
        ),
        (
            {
                "schedule": [
                    (0, 1, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 0, 3, 0),
                ],
            },
            True,
        ),
        (
            {
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 0, 1, 0),
                ],
            },
            False,
        ),
        (
            {
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 0, 2, 0),
                ],
            },
            False,
        ),
        (
            {
                "schedule": [
                    (0, 0, 1, 0),
                    (0, 0, 2, 0),
                ],
            },
            False,
        ),
        (
            {
                "schedule": [
                    (0, 0, 1, 0),
                    (0, 0, 3, 0),
                ],
            },
            False,
        ),
        (
            {
                "schedule": [
                    (0, 0, 2, 0),
                    (0, 0, 3, 0),
                ],
            },
            False,
        ),
    ],
)
def test_is_max_assignments_per_day_with_exception_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_max_assignments_per_day_with_exception_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "restriction": {"type": "Night", "limit": 3},
                "schedule": [],
            },
            True,
        ),
        (
            {
                "restriction": {"type": "Night", "limit": 3},
                "schedule": [
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 5, 3, 0),
                    (0, 6, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "restriction": {"type": "Night", "limit": 3},
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 3, 3, 0),
                ],
            },
            False,
        ),
        (
            {
                "restriction": {"type": "Night", "limit": 3},
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
    ],
)
def test_is_maximum_shifts_of_specific_type_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["sc_data"]["nurses"][0]["restrictions"] = [
        input_data["restriction"]
    ]

    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)

    # Execute
    retval = validator._is_maximum_shifts_of_specific_type_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "schedule": [],
            },
            True,
        ),
        (
            {
                "schedule": [
                    (0, 0, 3, 0),
                ],
            },
            False,
        ),
        (
            {
                "schedule": [
                    (0, 6, 3, 0),
                ],
            },
            False,
        ),
        (
            {
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
    ],
)
def test_is_planned_vacations_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["all_wd_data"][0]["vacations"] = ["HN_0"]
    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)
    # Execute
    retval = validator._is_planned_vacations_satisfied()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "requirements": [
                    {
                        "shiftType": "Early",
                        "skill": "HeadNurse",
                        "requirementOnMonday": {"minimum": 0, "optimal": 0},
                        "requirementOnTuesday": {"minimum": 0, "optimal": 0},
                        "requirementOnWednesday": {"minimum": 0, "optimal": 1},
                        "requirementOnThursday": {"minimum": 0, "optimal": 0},
                        "requirementOnFriday": {"minimum": 0, "optimal": 1},
                        "requirementOnSaturday": {"minimum": 0, "optimal": 1},
                        "requirementOnSunday": {"minimum": 0, "optimal": 0},
                    }
                ],
                "schedule": [],
            },
            True,
        ),
        (
            {
                "requirements": [
                    {
                        "shiftType": "Early",
                        "skill": "HeadNurse",
                        "requirementOnMonday": {"minimum": 0, "optimal": 0},
                        "requirementOnTuesday": {"minimum": 0, "optimal": 0},
                        "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                        "requirementOnThursday": {"minimum": 0, "optimal": 0},
                        "requirementOnFriday": {"minimum": 1, "optimal": 1},
                        "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                        "requirementOnSunday": {"minimum": 0, "optimal": 0},
                    }
                ],
                "schedule": [
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 5, 0, 0),
                ],
            },
            True,
        ),
        (
            {
                "requirements": [
                    {
                        "shiftType": "Early",
                        "skill": "HeadNurse",
                        "requirementOnMonday": {"minimum": 0, "optimal": 0},
                        "requirementOnTuesday": {"minimum": 0, "optimal": 0},
                        "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                        "requirementOnThursday": {"minimum": 0, "optimal": 0},
                        "requirementOnFriday": {"minimum": 2, "optimal": 1},
                        "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                        "requirementOnSunday": {"minimum": 0, "optimal": 0},
                    }
                ],
                "schedule": [
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                    (0, 3, 0, 0),
                ],
            },
            False,
        ),
        (
            {
                "requirements": [
                    {
                        "shiftType": "Early",
                        "skill": "HeadNurse",
                        "requirementOnMonday": {"minimum": 0, "optimal": 0},
                        "requirementOnTuesday": {"minimum": 0, "optimal": 0},
                        "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                        "requirementOnThursday": {"minimum": 0, "optimal": 0},
                        "requirementOnFriday": {"minimum": 1, "optimal": 1},
                        "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                        "requirementOnSunday": {"minimum": 0, "optimal": 0},
                    }
                ],
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
    ],
)
def test_is_minimal_capacity_satisfied(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["all_wd_data"][0]["requirements"] = input_data["requirements"]
    validator = ScheduleValidator()
    validator._init_variables(schedule, constants_for_1_nurse)
    # Execute
    retval = validator._is_minimal_capacity_satisfied()

    # Assert
    assert retval == expected
