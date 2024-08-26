"""
Tests for solver
"""

from nsp_solver.utils import utils
from nsp_solver.solver.nsp_cplex import compute_one_week
from nsp_solver.simulator.history_simulator import HistorySimulator
from nsp_solver.validator.validator import ScheduleValidator
import pytest
from contextlib import nullcontext as does_not_raise


@pytest.mark.parametrize(
    "input_data",
    [
        (
            {
                "history_file_id": 0,
                "weeks_files_ids": [3, 5, 6, 1],
            }
        ),
        (
            {
                "history_file_id": 0,
                "weeks_files_ids": [4, 9, 6, 7],
            }
        ),
        (
            {
                "history_file_id": 0,
                "weeks_files_ids": [4, 9, 7, 6],
            }
        ),
        (
            {
                "history_file_id": 0,
                "weeks_files_ids": [8, 6, 0, 8],
            }
        ),
        (
            {
                "history_file_id": 0,
                "weeks_files_ids": [9, 1, 7, 5],
            }
        ),
        (
            {
                "history_file_id": 1,
                "weeks_files_ids": [1, 3, 8, 8],
            }
        ),
        (
            {
                "history_file_id": 2,
                "weeks_files_ids": [0, 5, 6, 8],
            }
        ),
        (
            {
                "history_file_id": 2,
                "weeks_files_ids": [3, 5, 8, 2],
            }
        ),
        (
            {
                "history_file_id": 2,
                "weeks_files_ids": [5, 8, 2, 5],
            }
        ),

    ],
)
def test_solver(input_data, integration_tests_data_generator):
    # Arrange
    data = integration_tests_data_generator.get_data(input_data["history_file_id"], input_data["weeks_files_ids"])
    results = {}
    for w in data["all_weeks"]:
        for n in data["all_nurses"]:
            for d in data["all_days"]:
                for s in data["all_shifts"]:
                    for sk in data["all_skills"]:
                        results[(n, d + 7 * w, s, sk)] = 0
    time_limit_for_week = 2
    fail = False

    # Execute
    with does_not_raise():
        for week_number in data["all_weeks"]:
            data["wd_data"] = data["all_wd_data"][week_number]
            compute_one_week(time_limit_for_week, data, results)
            if results[(week_number, "status")] == utils.STATUS_FAIL:
                fail = True
                break
            simulator = HistorySimulator()
            simulator.update_history_for_next_week(results, data, week_number)
        if fail:
            total_value = 99999
        else:
            validator = ScheduleValidator(results, data)
            total_value = validator.evaluate_schedule()

    # Assert
    assert total_value < 99999
