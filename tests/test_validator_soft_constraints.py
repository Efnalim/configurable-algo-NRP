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


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignments": 3,
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
                "minimumNumberOfConsecutiveAssignments": 3,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 5, 0, 0),
                ],
            },
            2 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 3,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [(0, 0, 0, 0)],
            },
            1 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 3,
                "numberOfConsecutiveAssignments": 1,
                "schedule": [],
            },
            2 * utils.CONS_SHIFT_WEIGHT,
        ),
        (
            {
                "lastAssignedShiftType": "Early",
                "minimumNumberOfConsecutiveAssignments": 3,
                "numberOfConsecutiveAssignments": 3,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignments": 3,
                "numberOfConsecutiveAssignments": 0,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "lastAssignedShiftType": "None",
                "minimumNumberOfConsecutiveAssignments": 3,
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
    # print(f'mincons{constants_for_1_nurse["sc_data"]["shiftTypes"][0]["minimumNumberOfConsecutiveAssignments"]}')

    validator = ScheduleValidator(schedule, constants_for_1_nurse)
    print(
        validator.constants["h0_data_original"]["nurseHistory"][0][
            "numberOfConsecutiveAssignments"
        ]
    )

    # Execute
    retval = validator.get_min_consecutive_shifts_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 0,
                    "placement": utils.Shift_placement.START,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 1,
                    "placement": utils.Shift_placement.MID,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 5,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 5,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 6,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 6,
                    "placement": utils.Shift_placement.END,
                },
            },
            1 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 6,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 5,
                    "placement": utils.Shift_placement.MID,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 5,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 1,
                    "placement": utils.Shift_placement.START,
                },
            },
            1 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 0,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 6,
                    "placement": utils.Shift_placement.MID,
                },
            },
            1 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 6,
                    "placement": utils.Shift_placement.MID,
                },
            },
            1 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 5,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 5,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 5,
                    "placement": utils.Shift_placement.START,
                },
            },
            1 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 5,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 6,
                    "placement": utils.Shift_placement.START,
                },
            },
            6 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 6,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 0,
                    "placement": utils.Shift_placement.START,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 5,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 0,
                    "placement": utils.Shift_placement.MID,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 6,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 1,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 6,
                    "placement": utils.Shift_placement.END,
                },
            },
            1 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 1,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
    ],
)
def test_get_max_consecutive_days_off_value(
    input_data,
    expected,
    constants_for_1_nurse,
    results_1nurse_1full_week,
    schedule_modifier,
):
    # Arrange
    schedule = results_1nurse_1full_week
    schedule_modifier.remove_shifts(
        schedule,
        0,
        0,
        input_data["schedule"]["placement"],
        input_data["schedule"]["numberOfConsecutiveDaysOff"],
    )
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveDaysOff"
    ] = input_data["numberOfConsecutiveDaysOff"]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfConsecutiveDaysOff"] = input_data[
        "maximumNumberOfConsecutiveDaysOff"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_max_consecutive_days_off_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 0,
                    "placement": utils.Shift_placement.START,
                },
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 1,
                    "placement": utils.Shift_placement.MID,
                },
            },
            2 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 2,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 2,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 2,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 1,
                    "placement": utils.Shift_placement.START,
                },
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 0,
                    "placement": utils.Shift_placement.END,
                },
            },
            1 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 2,
                    "placement": utils.Shift_placement.MID,
                },
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 1,
                    "placement": utils.Shift_placement.END,
                },
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 2,
                    "placement": utils.Shift_placement.START,
                },
            },
            0,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveDaysOff": 2,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 0,
                    "placement": utils.Shift_placement.MID,
                },
            },
            0,
        ),
    ],
)
def test_get_min_consecutive_days_off_value(
    input_data,
    expected,
    constants_for_1_nurse,
    results_1nurse_1full_week,
    schedule_modifier,
):
    # Arrange
    schedule = results_1nurse_1full_week
    schedule_modifier.remove_shifts(
        schedule,
        0,
        0,
        input_data["schedule"]["placement"],
        input_data["schedule"]["numberOfConsecutiveDaysOff"],
    )
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveDaysOff"
    ] = input_data["numberOfConsecutiveDaysOff"]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["minimumNumberOfConsecutiveDaysOff"] = input_data[
        "minimumNumberOfConsecutiveDaysOff"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_min_consecutive_days_off_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 1,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 6,
                    "placement": utils.Shift_placement.END,
                },
            },
            2 * utils.CONS_DAY_OFF_WEIGHT,
        ),
        (
            {
                "minimumNumberOfConsecutiveDaysOff": 2,
                "maximumNumberOfConsecutiveDaysOff": 5,
                "numberOfConsecutiveDaysOff": 0,
                "schedule": {
                    "numberOfConsecutiveDaysOff": 4,
                    "placement": utils.Shift_placement.START,
                },
            },
            0,
        ),
    ],
)
def test_get_consecutive_days_off_value(
    input_data,
    expected,
    constants_for_1_nurse,
    results_1nurse_1full_week,
    schedule_modifier,
):
    # Arrange
    schedule = results_1nurse_1full_week
    schedule_modifier.remove_shifts(
        schedule,
        0,
        0,
        input_data["schedule"]["placement"],
        input_data["schedule"]["numberOfConsecutiveDaysOff"],
    )
    constants_for_1_nurse["h0_data_original"]["nurseHistory"][0][
        "numberOfConsecutiveDaysOff"
    ] = input_data["numberOfConsecutiveDaysOff"]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["minimumNumberOfConsecutiveDaysOff"] = input_data[
        "minimumNumberOfConsecutiveDaysOff"
    ]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfConsecutiveDaysOff"] = input_data[
        "maximumNumberOfConsecutiveDaysOff"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_consecutive_days_off_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "preferences": [],
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
                "preferences": [
                    {"nurse": "HN_0", "shiftType": "Early", "day": "Monday"}
                ],
                "schedule": [
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
                "preferences": [
                    {"nurse": "HN_0", "shiftType": "Early", "day": "Monday"},
                    {"nurse": "HN_0", "shiftType": "Night", "day": "Tuesday"},
                ],
                "schedule": [
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
                "preferences": [
                    {"nurse": "HN_0", "shiftType": "Any", "day": "Monday"},
                    {"nurse": "HN_0", "shiftType": "Night", "day": "Tuesday"},
                ],
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            1 * utils.UNSATISFIED_PREFERENCE_WEIGHT,
        ),
        (
            {
                "preferences": [
                    {"nurse": "HN_0", "shiftType": "Any", "day": "Monday"},
                ],
                "schedule": [
                    (0, 0, 3, 0),
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            1 * utils.UNSATISFIED_PREFERENCE_WEIGHT,
        ),
        (
            {
                "preferences": [
                    {"nurse": "HN_0", "shiftType": "Any", "day": "Monday"},
                    {"nurse": "HN_0", "shiftType": "Night", "day": "Tuesday"},
                ],
                "schedule": [
                    (0, 1, 0, 0),
                    (0, 2, 0, 0),
                    (0, 3, 0, 0),
                    (0, 4, 0, 0),
                ],
            },
            0,
        ),
    ],
)
def test_get_assignment_preferences_value(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["all_wd_data"][0]["shiftOffRequests"] = input_data[
        "preferences"
    ]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_assignment_preferences_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "completeWeekends": 0,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "completeWeekends": 1,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "completeWeekends": 1,
                "schedule": [
                    (0, 5, 0, 0),
                ],
            },
            1 * utils.INCOMPLETE_WEEKEDN_WEIGHT,
        ),
        (
            {
                "completeWeekends": 0,
                "schedule": [
                    (0, 5, 0, 0),
                ],
            },
            0,
        ),
        (
            {
                "completeWeekends": 0,
                "schedule": [
                    (0, 6, 0, 0),
                ],
            },
            0,
        ),
        (
            {
                "completeWeekends": 1,
                "schedule": [
                    (0, 6, 0, 0),
                ],
            },
            1 * utils.INCOMPLETE_WEEKEDN_WEIGHT,
        ),
        (
            {
                "completeWeekends": 1,
                "schedule": [
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            0,
        ),
        (
            {
                "completeWeekends": 0,
                "schedule": [
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            0,
        ),
    ],
)
def test_get_incomplete_weekends_value(
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
    ]["completeWeekends"] = input_data["completeWeekends"]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_incomplete_weekends_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "minimumNumberOfAssignments": 2,
                "maximumNumberOfAssignments": 4,
                "workingDays": 0,
            },
            2 * utils.TOTAL_ASSIGNMENTS_WEIGHT,
        ),
        (
            {
                "minimumNumberOfAssignments": 2,
                "maximumNumberOfAssignments": 4,
                "workingDays": 1,
            },
            1 * utils.TOTAL_ASSIGNMENTS_WEIGHT,
        ),
        (
            {
                "minimumNumberOfAssignments": 2,
                "maximumNumberOfAssignments": 4,
                "workingDays": 2,
            },
            0,
        ),
        (
            {
                "minimumNumberOfAssignments": 2,
                "maximumNumberOfAssignments": 4,
                "workingDays": 4,
            },
            0,
        ),
        (
            {
                "minimumNumberOfAssignments": 2,
                "maximumNumberOfAssignments": 4,
                "workingDays": 5,
            },
            1 * utils.TOTAL_ASSIGNMENTS_WEIGHT,
        ),
        (
            {
                "minimumNumberOfAssignments": 2,
                "maximumNumberOfAssignments": 4,
                "workingDays": 6,
            },
            2 * utils.TOTAL_ASSIGNMENTS_WEIGHT,
        ),
    ],
)
def test_get_total_assignments_out_of_limits_value(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
    schedule_modifier
):
    # Arrange
    schedule = empty_results_1nurse_1week
    schedule_modifier.add_shifts(
        schedule,
        0,
        0,
        utils.Shift_placement.START,
        input_data["workingDays"],
    )
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["minimumNumberOfAssignments"] = input_data["minimumNumberOfAssignments"]
    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfAssignments"] = input_data["maximumNumberOfAssignments"]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_total_assignments_out_of_limits_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "maximumNumberOfWorkingWeekends": 0,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "maximumNumberOfWorkingWeekends": 0,
                "schedule": [
                    (0, 5, 0, 0),
                ],
            },
            1 * utils.TOTAL_WORKING_WEEKENDS_WEIGHT,
        ),
        (
            {
                "maximumNumberOfWorkingWeekends": 0,
                "schedule": [
                    (0, 6, 0, 0),
                ],
            },
            1 * utils.TOTAL_WORKING_WEEKENDS_WEIGHT,
        ),
        (
            {
                "maximumNumberOfWorkingWeekends": 0,
                "schedule": [
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            1 * utils.TOTAL_WORKING_WEEKENDS_WEIGHT,
        ),
        (
            {
                "maximumNumberOfWorkingWeekends": 1,
                "schedule": [],
            },
            0,
        ),
        (
            {
                "maximumNumberOfWorkingWeekends": 1,
                "schedule": [
                    (0, 5, 0, 0),
                ],
            },
            0,
        ),
        (
            {
                "maximumNumberOfWorkingWeekends": 1,
                "schedule": [
                    (0, 6, 0, 0),
                ],
            },
            0,
        ),
        (
            {
                "maximumNumberOfWorkingWeekends": 1,
                "schedule": [
                    (0, 5, 0, 0),
                    (0, 6, 0, 0),
                ],
            },
            0,
        ),
    ],
)
def test_get_total_weekends_over_limit_value(
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
    ]["maximumNumberOfWorkingWeekends"] = input_data["maximumNumberOfWorkingWeekends"]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_total_weekends_over_limit_value()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "ifneeded_skills": [],
                "schedule": [],
            },
            0,
        ),
        (
            {
                "ifneeded_skills": [],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 1, 1),
                    (0, 2, 2, 2),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                    (0, 5, 2, 1),
                    (0, 6, 2, 2),
                ],
            },
            0,
        ),
        (
            {
                "ifneeded_skills": ["Caretaker"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 1, 1, 1),
                    (0, 2, 2, 2),
                    (0, 3, 3, 0),
                    (0, 4, 3, 0),
                    (0, 5, 2, 1),
                    (0, 6, 2, 2),
                ],
            },
            2 * utils.TOTAL_IFNEEDED_SKILL_WEIGHT,
        ),
        (
            {
                "ifneeded_skills": ["Caretaker"],
                "schedule": [],
            },
            0,
        ),
    ],
)
def test_get_total_uses_of_ifneeded_skills_value(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1
    constants_for_1_nurse["sc_data"]["nurses"][0]["skillsIfNeeded"] = input_data["ifneeded_skills"]
    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_total_uses_of_ifneeded_skills_value()

    # Assert
    assert retval == expected
