#!/usr/bin/python

import sys
import json

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import math
import time
import copy


from nsp_solver.solver.nsp_contest import compute_one_week as compute_one_week_or_tools
from nsp_solver.solver.nsp_cplex import compute_one_week as compute_one_week_cplex
from nsp_solver.solver.nsp_docplex import compute_one_week as compute_one_week_docplex
from nsp_solver.simulator.simulator import update_history_for_next_week
from nsp_solver.validator.validator import ScheduleValidator


def load_data(
    number_nurses: int,
    number_weeks: int,
    history_data_file_id: int,
    week_data_files_ids: list,
    config_data_file_id: int,
):
    """
    Loads and prepairs data for computation.
    Returns a dictionary named 'constants' containing loaded data.
    """

    path = "modified_data"
    file_name = path + f"\C{config_data_file_id}.json"
    f3 = open(file_name)
    config_data = json.load(f3)
    f3.close()

    file_name = (
        path
        + "\H0-n0"
        + str(number_nurses)
        + "w"
        + str(number_weeks)
        + "-"
        + str(history_data_file_id)
        + ".json"
    )
    f0 = open(file_name)
    h0_data = json.load(f0)
    f0.close()

    file_name = path + "\Sc-n0" + str(number_nurses) + "w" + str(number_weeks) + ".json"
    f1 = open(file_name)
    sc_data = json.load(f1)
    f1.close()

    wd_data = []
    for week in range(number_weeks):
        file_name = (
            path
            + "\WD-n0"
            + str(number_nurses)
            + "w"
            + str(number_weeks)
            + "-"
            + str(week_data_files_ids[week])
            + ".json"
        )
        f2 = open(file_name)
        wd_data.append(json.load(f2))
        f2.close()

    # initialize constants
    num_nurses = len(sc_data["nurses"])
    num_shifts = len(sc_data["shiftTypes"])
    num_skills = len(sc_data["skills"])
    num_days = 7
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_skills = range(num_skills)
    all_weeks = range(number_weeks)

    constants = {}
    constants["configuration"] = config_data
    constants["h0_data"] = h0_data
    constants["h0_data_original"] = copy.deepcopy(h0_data)
    constants["sc_data"] = sc_data
    constants["wd_data"] = wd_data[0]
    constants["all_wd_data"] = wd_data
    constants["num_nurses"] = num_nurses
    constants["num_shifts"] = num_shifts
    constants["num_skills"] = num_skills
    constants["num_days"] = num_days
    constants["num_weeks"] = number_weeks
    constants["all_nurses"] = all_nurses
    constants["all_shifts"] = all_shifts
    constants["all_days"] = all_days
    constants["all_skills"] = all_skills
    constants["all_weeks"] = all_weeks

    return constants


def display_schedule(results, constants, number_weeks, save, filename):
    """
    Displays computed schedule as table in a figure.
    """

    num_days = constants["num_days"] * number_weeks
    num_nurses = constants["num_nurses"]
    num_skills = constants["num_skills"]
    num_shifts = constants["num_shifts"]
    num_days_in_week = constants["num_days"]

    schedule_table = np.zeros([num_nurses, num_days * num_shifts])
    legend = np.zeros([1, num_skills + 2])

    for d in range(num_days):
        for n in range(num_nurses):
            for s in range(num_shifts):
                for sk in range(num_skills):
                    if results[(n, d, s, sk)] == 1:
                        schedule_table[n][d * num_shifts + s] = 0.85 - (0.175 * sk)

    # for w in range(number_weeks):
    #     for n in constants["all_wd_data"][w]["vacations"]:
    #         # n = int(nurse_id.split("_")[1])
    #         for d in range(num_days_in_week):
    #             for s in range(num_shifts):
    #                 schedule_table[n][(d + 7 * w)*num_shifts + s] = 1

    for sk in range(num_skills):
        legend[0][sk] = 0.85 - (0.175 * sk)
    legend[0][num_skills + 1] = 1

    fig, (ax0, ax1) = plt.subplots(
        2, 1, figsize=(16, 9), gridspec_kw={"height_ratios": [10, 1]}
    )

    c = ax0.pcolor(schedule_table)
    ax0.set_title("Schedule")
    ax0.set_xticks(np.arange(num_days * num_shifts))
    ax0.set_xticklabels(np.arange(num_days * num_shifts) / 4)

    ax0.xaxis.set_major_locator(ticker.MultipleLocator(4))

    c = ax1.pcolor(legend, edgecolors="k", linewidths=5)
    ax1.set_title("Legend - skills")
    ax1.set_xticks(np.arange(num_skills + 2) + 0.5)
    ax1.set_xticklabels(
        ["HeadNurse", "Nurse", "Caretaker", "Trainee", "Not working", "Vacation"]
    )

    fig.tight_layout()
    if save:
        plt.savefig(filename)
    else:
        plt.show()


def main(
    time_limit_for_week,
    mode,
    number_nurses: int,
    number_weeks: int,
    history_data_file_id: int,
    week_data_files_ids: list,
    config_data_file_id: int,
):
    # Loading Data and init constants
    constants = load_data(
        number_nurses,
        number_weeks,
        history_data_file_id,
        week_data_files_ids,
        config_data_file_id,
    )
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    if mode == 0:
        print(
            f"configuration: ILP-w{number_weeks}_n{number_nurses}_h{history_data_file_id}_{' '.join(map(str, week_data_files_ids))}"
        )
    if mode == 1:
        print(
            f"configuration: OR_TOOLS-w{number_weeks}_n{number_nurses}_h{history_data_file_id}_{' '.join(map(str, week_data_files_ids))}"
        )
    if mode == 2:
        print(
            f"configuration: CPLEX-w{number_weeks}_n{number_nurses}_h{history_data_file_id}_{' '.join(map(str, week_data_files_ids))}"
        )

    display = True
    if time_limit_for_week == 0:
        display = False
        time_limit_for_week = 10 + 10 * (constants["num_nurses"] - 20)
        # time_limit_for_week = 10

    # accumulate results over weeks
    start = time.time()
    results = {}
    for week_number in range(number_weeks):
        constants["wd_data"] = constants["all_wd_data"][week_number]
        if mode == 0:
            compute_one_week_cplex(time_limit_for_week, constants, results)
        if mode == 1:
            compute_one_week_or_tools(
                time_limit_for_week, week_number, constants, results
            )
        if mode == 2:
            compute_one_week_docplex(
                time_limit_for_week, week_number, constants, results
            )
        update_history_for_next_week(results, constants, week_number)
    end = time.time()
    # display results
    if display:
        display_schedule(results, constants, number_weeks, False, None)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("----------------------------------------------------------------")
    validator = ScheduleValidator(results, constants, {})
    total_value = validator.evaluate_results()
    # print(f"configuration: n{number_nurses}_h{history_data_file_id}_w{number_weeks}_{"".join(map(str, week_data_files_ids))}")
    print(
        f'inputs: n{number_nurses}_h{history_data_file_id}_w{number_weeks}_{"".join(map(str, week_data_files_ids))}'
    )
    print(f"value total: {total_value}")
    print(f"time total: {math.ceil(end - start)} s")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    tool_name = ""
    if mode == 0:
        tool_name = "CPLEX"
    if mode == 1:
        tool_name = "OR TOOLS"
    if mode == 2:
        tool_name = "DOCPLEX"

    schedule_file_name = f'outputs\\schedules\\{tool_name}_n{number_nurses}_h{history_data_file_id}_w{number_weeks}_{"".join(map(str, week_data_files_ids))}.png'
    # with open(schedule_file_name, "w") as f:
    display_schedule(results, constants, number_weeks, True, schedule_file_name)
    # validator.export_schedule(f)


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
