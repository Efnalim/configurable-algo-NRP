#!/usr/bin/python

import math
import sys
import time

from nsp_solver.simulator.history_simulator import HistorySimulator
from nsp_solver.simulator.simulator import Simulator, SimulatorInput
from nsp_solver.solver.nsp_cplex import CplexSolver
from nsp_solver.solver.nsp_docplex import DOCPLEX_Solver
from nsp_solver.solver.nsp_or_tools import ORTOOLS_Solver
from nsp_solver.solver.nsp_solver import NSP_solver
from nsp_solver.validator.conf_validator import ConfigValidator
from nsp_solver.validator.validator import ScheduleValidator


def main(
    time_limit_for_week,
    mode,
    number_nurses: int,
    number_weeks: int,
    history_data_file_id: int,
    week_data_files_ids: list,
    config_data_file_id: int,
):
    solver: NSP_solver
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    if mode == 0:
        solver = CplexSolver()
        print(
            f"configuration: CPLEX-w{number_weeks}_n{number_nurses}_h{history_data_file_id}_{' '.join(map(str, week_data_files_ids))}"
        )
    if mode == 1:
        solver = ORTOOLS_Solver()
        print(
            f"configuration: OR_TOOLS-w{number_weeks}_n{number_nurses}_h{history_data_file_id}_{' '.join(map(str, week_data_files_ids))}"
        )
    if mode == 2:
        solver = DOCPLEX_Solver()
        print(
            f"configuration: DOCPLEX-w{number_weeks}_n{number_nurses}_h{history_data_file_id}_{' '.join(map(str, week_data_files_ids))}"
        )

    if time_limit_for_week == 0:
        time_limit_for_week = 10 + 10 * (number_nurses - 20)
        # time_limit_for_week = 10

    graph_file = f'outputs\\schedules\\{solver.name}_n{number_nurses}_h{history_data_file_id}_w{number_weeks}_{"".join(map(str, week_data_files_ids))}.png'
    validator_out_file = 'outputs/validator_result.txt'
    # accumulate results over weeks
    path = "modified_data"
    config_file = path + f"\C{config_data_file_id}.json"
    hist_file = (
        path + f"\H0-n0{number_nurses}w{number_weeks}-{history_data_file_id}.json"
    )
    scen_file = path + f"\Sc-n0{number_nurses}w{number_weeks}.json"
    wd_files = []
    for week in range(number_weeks):
        wd_files.append(
            path
            + f"\WD-n0{number_nurses}w{number_weeks}-{week_data_files_ids[week]}.json"
        )

    simulator = Simulator()
    input = SimulatorInput(
        config_file,
        hist_file,
        scen_file,
        wd_files,
        time_limit_for_week,
        solver,
        ScheduleValidator(),
        ConfigValidator(),
        HistorySimulator(),
        graph_file,
        validator_out_file
    )
    start = time.time()
    total_value, _ = simulator.simulate_computation(input)
    end = time.time()

    # display results
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("----------------------------------------------------------------")
    # print(f"configuration: n{number_nurses}_h{history_data_file_id}_w{number_weeks}_{"".join(map(str, week_data_files_ids))}")
    with open("outputs/results.txt", "a") as file:
        file.write(solver.name.ljust(7))
        file.write(" | ")
        file.write(
            f'n0{number_nurses}_w{number_weeks}_h{history_data_file_id}_{"-".join(map(str, week_data_files_ids))}'
        )
        file.write(" | ")
        file.write(f"{total_value}".ljust(5))
        file.write(" | ")
        file.write(f"{math.ceil(end - start)} s".ljust(7) + "\n")


if __name__ == "__main__":
    time_limit_for_week = int(sys.argv[1])
    mode = int(sys.argv[2])
    number_nurses = int(sys.argv[3])
    config_data_file_id = int(sys.argv[4])
    number_weeks = int(sys.argv[5])
    history_data_file_id = int(sys.argv[6])
    week_data_files_ids = list(map(int, (sys.argv[7:])))
    main(
        time_limit_for_week,
        mode,
        number_nurses,
        number_weeks,
        history_data_file_id,
        week_data_files_ids,
        config_data_file_id,
    )
