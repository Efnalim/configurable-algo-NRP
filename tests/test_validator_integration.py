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
                "tested_constraints": [],
                "schedule": [],
            },
            True,
        ),
        (
            {
                "tested_constraints": ["h1"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 0, 0, 1),
                ],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h2"],
                "schedule": [],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h3"],
                "schedule": [(0, 0, 3, 0), (0, 1, 0, 0)],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h4"],
                "schedule": [(0, 0, 3, 3)],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h5"],
                "schedule": [(0, 1, 3, 0)],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h6"],
                "schedule": [(0, 1, 3, 0), (0, 3, 3, 0)],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h7"],
                "schedule": [(0, 5, 3, 0)],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h8"],
                "schedule": [],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h9"],
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
                "tested_constraints": ["h10"],
                "schedule": [(0, 0, 1, 0), (0, 0, 3, 0)],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h11"],
                "schedule": [(0, 0, 3, 0), (0, 1, 3, 0), (0, 2, 3, 0), (0, 3, 3, 0)],
            },
            False,
        ),
        (
            {
                "tested_constraints": ["h12"],
                "schedule": [(0, 0, 3, 0), (0, 1, 3, 0), (0, 2, 3, 0), (0, 3, 3, 0)],
            },
            False,
        ),
    ],
)
def test_is_schedule_valid(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
    all_false_config_data,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1

    constants_for_1_nurse["configuration"] = all_false_config_data
    for constr in input_data["tested_constraints"]:
        constants_for_1_nurse["configuration"][constr] = True

    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfIncompleteWeekendsHard"] = 0

    constants_for_1_nurse["sc_data"]["nurses"][0]["restrictions"] = [
        {"type": "Night", "limit": 3}
    ]
    constants_for_1_nurse["all_wd_data"][0]["vacations"] = ["HN_0"]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.is_schedule_valid()

    # Assert
    assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "tested_constraints": [],
                "schedule": [],
            },
            0,
        ),
        (
            {
                "tested_constraints": ["s1"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s2"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s3"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s4"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s5"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s6"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s7"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s8"],
                "schedule": [
                    (0, 0, 0, 2),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
        (
            {
                "tested_constraints": ["s9"],
                "schedule": [
                    (0, 0, 0, 0),
                    (0, 6, 0, 1),
                ],
            },
            1,
        ),
    ],
)
def test_get_objective_value_of_schedule(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
    all_false_config_data,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1

    constants_for_1_nurse["configuration"] = all_false_config_data
    for constr in input_data["tested_constraints"]:
        constants_for_1_nurse["configuration"][constr] = True

    constants_for_1_nurse["sc_data"]["contracts"][
        utils.contract_to_int[constants_for_1_nurse["sc_data"]["nurses"][0]["contract"]]
    ]["maximumNumberOfWorkingWeekends"] = 0

    # constants_for_1_nurse["sc_data"]["nurses"][0]["restrictions"] = [{"type": "Night", "limit": 3}]
    constants_for_1_nurse["all_wd_data"][0]["shiftOffRequests"] = [
        {"nurse": "HN_0", "shiftType": "Any", "day": "Monday"}
    ]

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.get_objective_value_of_schedule()

    # Assert
    if expected > 0:
        assert retval > 0
    else:
        assert retval == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            {
                "tested_constraints": [],
                "schedule": [],
            },
            0,
        ),
        (
            {
                "tested_constraints": ["h2"],
                "schedule": [],
            },
            99999,
        ),
    ],
)
def test_evaluate_results(
    input_data,
    expected,
    constants_for_1_nurse,
    empty_results_1nurse_1week,
    all_false_config_data,
):
    # Arrange
    schedule = empty_results_1nurse_1week
    for input in input_data["schedule"]:
        schedule[input] = 1

    constants_for_1_nurse["configuration"] = all_false_config_data
    for constr in input_data["tested_constraints"]:
        constants_for_1_nurse["configuration"][constr] = True

    validator = ScheduleValidator(schedule, constants_for_1_nurse)

    # Execute
    retval = validator.evaluate_results()

    # Assert
    if expected > 0:
        assert retval > 0
    else:
        assert retval == expected
