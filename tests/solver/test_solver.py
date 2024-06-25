"""
Tests for solver
"""

from nsp_solver.utils import utils
from nsp_solver.solver.nsp_cplex import compute_one_week
from nsp_solver.simulator.simulator import HistorySimulator
from nsp_solver.validator.validator import ScheduleValidator
import pytest


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
def test_solver(input_data, integration_tests_constants_generator):
    # Arrange
    constants = integration_tests_constants_generator.get_constants(input_data["history_file_id"], input_data["weeks_files_ids"])
    results = {}
    for w in constants["all_weeks"]:
        for n in constants["all_nurses"]:
            for d in constants["all_days"]:
                for s in constants["all_shifts"]:
                    for sk in constants["all_skills"]:
                        results[(n, d + 7 * w, s, sk)] = 0
    time_limit_for_week = 10
    fail = False

    # Execute
    for week_number in constants["all_weeks"]:
        constants["wd_data"] = constants["all_wd_data"][week_number]
        compute_one_week(time_limit_for_week, constants, results)
        if results[(week_number, "status")] == utils.STATUS_FAIL:
            fail = True
            break
        simulator = HistorySimulator()
        simulator.update_history_for_next_week(results, constants, week_number)
    if fail:
        total_value = 99999
    else:
        validator = ScheduleValidator(results, constants)
        total_value = validator.evaluate_results()

    # Assert
    assert total_value < 99999
