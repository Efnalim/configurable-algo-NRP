from nsp_solver.simulator.history_simulator import HistorySimulator
import numpy as np
import pytest

"""
Tests for simulator.py
"""


def test_compute_helpful_values__1nurse_5shifts_5_days(
    data_for_1_nurse, empty_results_1nurse_1week
):
    # Arrange
    results = empty_results_1nurse_1week
    results[(0, 0, 0, 0)] = 1
    results[(0, 1, 1, 1)] = 1
    results[(0, 2, 2, 2)] = 1
    results[(0, 3, 1, 1)] = 1
    results[(0, 4, 0, 0)] = 1
    simulator = HistorySimulator()

    # Act
    working_days, shifts = simulator._compute_helpful_values(
        results, data_for_1_nurse, 0
    )

    # Assert
    assert working_days[0][0] == 1
    assert working_days[0][1] == 1
    assert working_days[0][2] == 1
    assert working_days[0][3] == 1
    assert working_days[0][4] == 1
    assert np.sum(np.array(working_days)) == 5

    assert shifts[0][0][0] == 1
    assert shifts[0][1][1] == 1
    assert shifts[0][2][2] == 1
    assert shifts[0][3][1] == 1
    assert shifts[0][4][0] == 1
    assert np.sum(np.array(shifts)) == 5


def test_compute_helpful_values__1nurse_5shifts_4_days(
    data_for_1_nurse, empty_results_1nurse_1week
):
    """This is a mock test"""
    # Arrange
    results = empty_results_1nurse_1week
    results[(0, 0, 0, 0)] = 1
    results[(0, 0, 3, 0)] = 1
    results[(0, 1, 1, 1)] = 1
    results[(0, 2, 2, 2)] = 1
    results[(0, 3, 1, 1)] = 1
    simulator = HistorySimulator()

    # Act
    working_days, shifts = simulator._compute_helpful_values(
        results, data_for_1_nurse, 0
    )

    # Assert
    assert working_days[0][0] == 1
    assert working_days[0][1] == 1
    assert working_days[0][2] == 1
    assert working_days[0][3] == 1
    assert np.sum(np.array(working_days)) == 4

    assert shifts[0][0][0] == 1
    assert shifts[0][0][3] == 1
    assert shifts[0][1][1] == 1
    assert shifts[0][2][2] == 1
    assert shifts[0][3][1] == 1
    assert np.sum(np.array(shifts)) == 5


def test_compute_helpful_values__1nurse_0shifts(
    data_for_1_nurse, empty_results_1nurse_1week
):
    """This is a mock test"""
    # Arrange
    results = empty_results_1nurse_1week
    simulator = HistorySimulator()

    # Act
    working_days, shifts = simulator._compute_helpful_values(
        results, data_for_1_nurse, 0
    )

    # Assert
    assert np.sum(np.array(working_days)) == 0
    assert np.sum(np.array(shifts)) == 0


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            [(0, 0, 3, 0), (0, 1, 3, 0), (0, 2, 3, 0), (0, 3, 3, 0), (0, 4, 3, 0)],
            {
                "numberOfAssignments": 5,
                "numberOfWorkingWeekends": 0,
                "numberOfIncompleteWeekends": 0,
            },
        ),
        (
            [],
            {
                "numberOfAssignments": 0,
                "numberOfWorkingWeekends": 0,
                "numberOfIncompleteWeekends": 0,
            },
        ),
        (
            [(0, 1, 3, 0), (0, 2, 3, 0), (0, 3, 3, 0), (0, 4, 3, 0), (0, 5, 3, 0)],
            {
                "numberOfAssignments": 5,
                "numberOfWorkingWeekends": 1,
                "numberOfIncompleteWeekends": 1,
            },
        ),
        (
            [(0, 4, 3, 0), (0, 5, 3, 0), (0, 6, 3, 0)],
            {
                "numberOfAssignments": 3,
                "numberOfWorkingWeekends": 1,
                "numberOfIncompleteWeekends": 0,
            },
        ),
    ],
)
def test_update_cumulative_data__1nurse(
    input_data, expected, data_for_1_nurse, empty_results_1nurse_1week
):
    """This is a mock test"""
    # Arrange
    results = empty_results_1nurse_1week
    for input in input_data:
        results[input] = 1
    simulator = HistorySimulator()
    working_days, shifts = simulator._compute_helpful_values(
        results, data_for_1_nurse, 0
    )

    # Act
    simulator._update_cumulative_data(data_for_1_nurse, working_days, shifts)

    # Assert
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0]["numberOfAssignments"]
        == expected["numberOfAssignments"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0]["numberOfWorkingWeekends"]
        == expected["numberOfWorkingWeekends"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfIncompleteWeekends"
        ]
        == expected["numberOfIncompleteWeekends"]
    )


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            [],
            {
                "numberOfConsecutiveDaysOff": 7,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
            },
        ),
        (
            [(0, 0, 3, 0), (0, 1, 3, 0), (0, 2, 3, 0), (0, 3, 3, 0), (0, 4, 3, 0)],
            {
                "numberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
            },
        ),
        (
            [(0, 5, 0, 0), (0, 6, 0, 0), (0, 6, 3, 0)],
            {
                "numberOfConsecutiveDaysOff": 0,
                "numberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveAssignments": 1,
                "lastAssignedShiftType": "Night",
            },
        ),
        (
            [(0, 4, 0, 0), (0, 5, 1, 0), (0, 6, 1, 0)],
            {
                "numberOfConsecutiveDaysOff": 0,
                "numberOfConsecutiveWorkingDays": 3,
                "numberOfConsecutiveAssignments": 2,
                "lastAssignedShiftType": "Day",
            },
        ),
        (
            [(0, 4, 2, 0), (0, 5, 2, 0), (0, 6, 2, 0)],
            {
                "numberOfConsecutiveDaysOff": 0,
                "numberOfConsecutiveWorkingDays": 3,
                "numberOfConsecutiveAssignments": 3,
                "lastAssignedShiftType": "Late",
            },
        ),
    ],
)
def test_update_border_data(
    input_data, expected, data_for_1_nurse, empty_results_1nurse_1week
):
    """This is a mock test"""
    # Arrange
    results = empty_results_1nurse_1week
    for input in input_data:
        results[input] = 1
    simulator = HistorySimulator()
    working_days, shifts = simulator._compute_helpful_values(
        results, data_for_1_nurse, 0
    )
    # Act
    simulator._update_border_data(data_for_1_nurse, working_days, shifts)

    # Assert
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfConsecutiveDaysOff"
        ]
        == expected["numberOfConsecutiveDaysOff"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfConsecutiveWorkingDays"
        ]
        == expected["numberOfConsecutiveWorkingDays"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfConsecutiveAssignments"
        ]
        == expected["numberOfConsecutiveAssignments"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0]["lastAssignedShiftType"]
        == expected["lastAssignedShiftType"]
    )


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            [],
            {
                "numberOfAssignments": 0,
                "numberOfWorkingWeekends": 0,
                "numberOfIncompleteWeekends": 0,
                "numberOfConsecutiveDaysOff": 7,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
            },
        ),
        (
            [(0, 0, 3, 0), (0, 1, 3, 0), (0, 2, 3, 0), (0, 3, 3, 0), (0, 4, 3, 0)],
            {
                "numberOfAssignments": 5,
                "numberOfWorkingWeekends": 0,
                "numberOfIncompleteWeekends": 0,
                "numberOfConsecutiveDaysOff": 2,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveAssignments": 0,
                "lastAssignedShiftType": "None",
            },
        ),
        (
            [(0, 5, 0, 0), (0, 6, 0, 0), (0, 6, 3, 0)],
            {
                "numberOfAssignments": 3,
                "numberOfWorkingWeekends": 1,
                "numberOfIncompleteWeekends": 0,
                "numberOfConsecutiveDaysOff": 0,
                "numberOfConsecutiveWorkingDays": 2,
                "numberOfConsecutiveAssignments": 1,
                "lastAssignedShiftType": "Night",
            },
        ),
        (
            [(0, 4, 0, 0), (0, 5, 1, 0), (0, 6, 1, 0)],
            {
                "numberOfAssignments": 3,
                "numberOfWorkingWeekends": 1,
                "numberOfIncompleteWeekends": 0,
                "numberOfConsecutiveDaysOff": 0,
                "numberOfConsecutiveWorkingDays": 3,
                "numberOfConsecutiveAssignments": 2,
                "lastAssignedShiftType": "Day",
            },
        ),
        (
            [(0, 6, 2, 0)],
            {
                "numberOfAssignments": 1,
                "numberOfWorkingWeekends": 1,
                "numberOfIncompleteWeekends": 1,
                "numberOfConsecutiveDaysOff": 0,
                "numberOfConsecutiveWorkingDays": 1,
                "numberOfConsecutiveAssignments": 1,
                "lastAssignedShiftType": "Late",
            },
        ),
    ],
)
def test_update_history_for_next_week(
    input_data, expected, data_for_1_nurse, empty_results_1nurse_1week
):
    """This is a mock test"""
    # Arrange
    results = empty_results_1nurse_1week
    for input in input_data:
        results[input] = 1
    simulator = HistorySimulator()

    # Act
    simulator.update_history_for_next_week(results, data_for_1_nurse)

    # Assert
    assert data_for_1_nurse["h0_data"]["week"] == 1
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0]["numberOfAssignments"]
        == expected["numberOfAssignments"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0]["numberOfWorkingWeekends"]
        == expected["numberOfWorkingWeekends"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfIncompleteWeekends"
        ]
        == expected["numberOfIncompleteWeekends"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfConsecutiveDaysOff"
        ]
        == expected["numberOfConsecutiveDaysOff"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfConsecutiveWorkingDays"
        ]
        == expected["numberOfConsecutiveWorkingDays"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0][
            "numberOfConsecutiveAssignments"
        ]
        == expected["numberOfConsecutiveAssignments"]
    )
    assert (
        data_for_1_nurse["h0_data"]["nurseHistory"][0]["lastAssignedShiftType"]
        == expected["lastAssignedShiftType"]
    )
