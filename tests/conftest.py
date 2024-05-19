import copy
import json
import pytest

from src.nsp_solver.validator.validator import ScheduleValidator


# @pytest.fixture(scope="session")
@pytest.fixture
def constants_for_1_nurse():
    path = "tests\\test_data"
    file_name = path + "\\C1.json"
    f3 = open(file_name)
    config_data = json.load(f3)
    f3.close()

    file_name = path + "\\H0-n035w4-0.json"
    f0 = open(file_name)
    h0_data = json.load(f0)
    f0.close()

    file_name = path + "\\Sc-n035w4.json"
    f1 = open(file_name)
    sc_data = json.load(f1)
    f1.close()

    wd_data = []
    for week in range(4):
        file_name = (
            path
            + "\\WD-n035w4-"
            + str(week)
            + ".json"
        )
        f2 = open(file_name)
        wd_data.append(json.load(f2))
        f2.close()

    # initialize constants
    num_nurses = 1
    num_shifts = len(sc_data["shiftTypes"])
    num_skills = len(sc_data["skills"])
    num_days = 7
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_skills = range(num_skills)
    all_weeks = range(4)

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
    constants["num_weeks"] = 1
    constants["all_nurses"] = all_nurses
    constants["all_shifts"] = all_shifts
    constants["all_days"] = all_days
    constants["all_skills"] = all_skills
    constants["all_weeks"] = all_weeks

    return constants


@pytest.fixture
def empty_results_1nurse_1week(constants_for_1_nurse):
    num_days = constants_for_1_nurse["num_days"]
    num_nurses = constants_for_1_nurse["num_nurses"]
    num_skills = constants_for_1_nurse["num_skills"]
    num_shifts = constants_for_1_nurse["num_shifts"]
    week_number = 0

    results = {}

    for n in range(num_nurses):
        for d in range(num_days):
            for s in range(num_shifts):
                for sk in range(num_skills):
                    results[(n, d + 7 * week_number, s, sk)] = 0

    return results


@pytest.fixture
def validator_for_1nurse_1week(constants_for_1_nurse, empty_results_1nurse_1week):
    return ScheduleValidator(empty_results_1nurse_1week, constants_for_1_nurse)
