"""
Tests for solver
"""

from nsp_solver.utils import utils
import pytest

from src.nsp_solver.validator.validator import ScheduleValidator


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
                        "requirementOnWednesday": {"minimum": 0, "optimal": 0},
                        "requirementOnThursday": {"minimum": 0, "optimal": 0},
                        "requirementOnFriday": {"minimum": 0, "optimal": 0},
                        "requirementOnSaturday": {"minimum": 0, "optimal": 0},
                        "requirementOnSunday": {"minimum": 0, "optimal": 0},
                    }
                ],
                "schedule": [],
            },
            0,
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
            0,
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
                        "requirementOnFriday": {"minimum": 1, "optimal": 2},
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
            1 * utils.OPT_CAPACITY_WEIGHT,
        ),
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
            3 * utils.OPT_CAPACITY_WEIGHT,
        ),
    ],
)
def test_get_optimal_capacity_value(
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
    validator = ScheduleValidator(schedule, constants_for_1_nurse)
    # Execute
    retval = validator.get_optimal_capacity_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfConsecutiveWorkingDays": 5,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 3, 0),
                    (0, 2, 3, 0),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                ],
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDays": 5,
                "numberOfConsecutiveWorkingDays": 3,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDays": 5,
                "numberOfConsecutiveWorkingDays": 7,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDays": 5,
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
            2 * utils.CONS_WORK_DAY_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDays": 5,
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
            3 * utils.CONS_WORK_DAY_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveWorkingDays": 5,
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
            2 * utils.CONS_WORK_DAY_WEIGHT,
        ),
    ],
)
def test_get_max_consecutive_work_days_value(
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
    ]["maximumNumberOfConsecutiveWorkingDays"] = input_data[
        "maximumNumberOfConsecutiveWorkingDays"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_max_consecutive_work_days_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimumNumberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveWorkingDays": 1,
                "schedule": [],
            },
            1 * utils.CONS_WORK_DAY_WEIGHT,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveWorkingDays": 2,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveWorkingDays": 1,
                "schedule": [
                    (0, 0, 3, 0),
                ],
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDays": 2,
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
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveWorkingDays": 1,
                "schedule": [
                    (0, 1, 3, 0),
                    (0, 3, 3, 0),
                    (0, 5, 0, 0),
                ],
            },
            4 * utils.CONS_WORK_DAY_WEIGHT,
        ),
    ],
)
def test_get_min_consecutive_work_days_value(
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
    ]["minimumNumberOfConsecutiveWorkingDays"] = input_data[
        "minimumNumberOfConsecutiveWorkingDays"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_min_consecutive_work_days_value()

    # Assert
    assert retval == expected


@pytest.mark.skip(reason="not finished yet")
@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "lastAssignedShiftType": "None",
                "maximumNumberOfConsecutiveAssignments": 5,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "maximumNumberOfConsecutiveAssignments": 5,
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
            1 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "maximumNumberOfConsecutiveAssignments": 5,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "maximumNumberOfConsecutiveAssignments": 5,
                "numberOfConsecutiveAssignments": 5,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "maximumNumberOfConsecutiveAssignments": 5,
                "numberOfConsecutiveAssignments": 5,
                "schedule": [(0, 0, 0, 0)],
            },
            1 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "maximumNumberOfConsecutiveAssignments": 5,
                "numberOfConsecutiveAssignments": 1,
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
            3 * utils.CONS_SHIFT_WEIGHT,
        ),
    ],
)
def test_get_max_consecutive_shifts_value(
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
        "maximumNumberOfConsecutiveAssignments"
    ] = input_data["maximumNumberOfConsecutiveAssignments"]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_max_consecutive_shifts_value()

    # Assert
    assert retval == expected


@pytest.mark.skip(reason="not finished yet")
@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignments": 2,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 2,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 5, 0, 0),
                ],
            },
            3 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 2,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [(0, 0, 0, 0)],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 2,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [],
            },
            1 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 2,
                "numberOfConsecutiveAssignments": 2,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 2,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [(0, 0, 0, 0)],
            },
            1 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignments": 2,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [
                    (0, 6, 0, 0),
                ],
            },
            0,
        ),
    ],
)
def test_get_min_consecutive_shifts_value(
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
        "minimumNumberOfConsecutiveAssignments"
    ] = input_data["minimumNumberOfConsecutiveAssignments"]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_min_consecutive_shifts_value()

    # Assert
    assert retval == expected
