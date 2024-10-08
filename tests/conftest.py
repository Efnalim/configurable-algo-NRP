import copy
import json
from nsp_solver.utils import utils
import pytest

from src.nsp_solver.validator.validator import ScheduleValidator


# @pytest.fixture(scope="session")
@pytest.fixture
def data_for_1_nurse():
    config_data = {
        "h1": True,
        "h2": True,
        "h3": True,
        "h4": True,
        "h5": True,
        "h6": True,
        "h7": True,
        "h8": True,
        "h9": True,
        "h10": True,
        "h11": True,
        "h12": True,
        "s1": True,
        "s2": True,
        "s3": True,
        "s4": True,
        "s5": True,
        "s6": True,
        "s7": True,
        "s8": True,
        "s9": True,
    }

    h0_data = {
        "week": 0,
        "scenario": "n035w4",
        "nurseHistory": [
            {
                "nurse": "HN_0",
                "numberOfAssignments": 0,
                "numberOfWorkingWeekends": 0,
                "numberOfIncompleteWeekends": 0,
                "lastAssignedShiftType": "None",
                "numberOfConsecutiveAssignments": 0,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveDaysOff": 2,
                "numbersOfAssignedRestrictedShiftTypes": [
                    {"type:": "Early", "numberOfAssignments": 0},
                    {"type:": "Day", "numberOfAssignments": 0},
                    {"type:": "Late", "numberOfAssignments": 0},
                    {"type:": "Night", "numberOfAssignments": 0},
                ],
            }
        ],
    }

    sc_data = {
        "id": "n035w4",
        "numberOfWeeks": 4,
        "skills": ["HeadNurse", "Nurse", "Caretaker", "Trainee"],
        "shiftTypes": [
            {
                "id": "Early",
                "minimumNumberOfConsecutiveAssignments": 2,
                "maximumNumberOfConsecutiveAssignments": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 7,
            },
            {
                "id": "Day",
                "minimumNumberOfConsecutiveAssignments": 2,
                "maximumNumberOfConsecutiveAssignments": 7,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 10,
            },
            {
                "id": "Late",
                "minimumNumberOfConsecutiveAssignments": 2,
                "maximumNumberOfConsecutiveAssignments": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 2,
                "maximumNumberOfConsecutiveAssignmentsHard": 7,
            },
            {
                "id": "Night",
                "minimumNumberOfConsecutiveAssignments": 4,
                "maximumNumberOfConsecutiveAssignments": 5,
                "minimumNumberOfConsecutiveAssignmentsHard": 3,
                "maximumNumberOfConsecutiveAssignmentsHard": 7,
            },
        ],
        "forbiddenShiftTypeSuccessions": [
            {"precedingShiftType": "Early", "succeedingShiftTypes": []},
            {"precedingShiftType": "Day", "succeedingShiftTypes": []},
            {"precedingShiftType": "Late", "succeedingShiftTypes": ["Early", "Day"]},
            {
                "precedingShiftType": "Night",
                "succeedingShiftTypes": ["Early", "Day", "Late"],
            },
        ],
        "contracts": [
            {
                "id": "FullTime",
                "minimumNumberOfAssignments": 15,
                "maximumNumberOfAssignments": 22,
                "minimumNumberOfAssignmentsHard": 12,
                "maximumNumberOfAssignmentsHard": 25,
                "minimumNumberOfConsecutiveWorkingDays": 3,
                "maximumNumberOfConsecutiveWorkingDays": 5,
                "minimumNumberOfConsecutiveDaysOff": 2,
                "maximumNumberOfConsecutiveDaysOff": 3,
                "maximumNumberOfWorkingWeekends": 2,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "maximumNumberOfConsecutiveDaysOffHard": 5,
                "maximumNumberOfIncompleteWeekendsHard": 1,
                "minimalFreePeriod": 2,
                "completeWeekends": 1,
            },
            {
                "id": "PartTime",
                "minimumNumberOfAssignments": 7,
                "maximumNumberOfAssignments": 15,
                "minimumNumberOfAssignmentsHard": 4,
                "maximumNumberOfAssignmentsHard": 18,
                "minimumNumberOfConsecutiveWorkingDays": 3,
                "maximumNumberOfConsecutiveWorkingDays": 5,
                "minimumNumberOfConsecutiveDaysOff": 2,
                "maximumNumberOfConsecutiveDaysOff": 5,
                "maximumNumberOfWorkingWeekends": 2,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "maximumNumberOfConsecutiveDaysOffHard": 7,
                "maximumNumberOfIncompleteWeekendsHard": 1,
                "minimalFreePeriod": 2,
                "completeWeekends": 1,
            },
            {
                "id": "HalfTime",
                "minimumNumberOfAssignments": 5,
                "maximumNumberOfAssignments": 11,
                "minimumNumberOfAssignmentsHard": 4,
                "maximumNumberOfAssignmentsHard": 14,
                "minimumNumberOfConsecutiveWorkingDays": 3,
                "maximumNumberOfConsecutiveWorkingDays": 7,
                "minimumNumberOfConsecutiveDaysOff": 3,
                "maximumNumberOfConsecutiveDaysOff": 5,
                "maximumNumberOfWorkingWeekends": 1,
                "minimumNumberOfConsecutiveWorkingDaysHard": 2,
                "maximumNumberOfConsecutiveWorkingDaysHard": 7,
                "minimumNumberOfConsecutiveDaysOffHard": 2,
                "maximumNumberOfConsecutiveDaysOffHard": 7,
                "maximumNumberOfIncompleteWeekendsHard": 1,
                "minimalFreePeriod": 2,
                "completeWeekends": 1,
            },
        ],
        "nurses": [
            {
                "id": "HN_0",
                "contract": "HalfTime",
                "skills": ["HeadNurse", "Nurse", "Caretaker"],
                "skillsIfNeeded": ["Caretaker"],
                "restrictions": [],
                "wantedOvertime": 3,
            }
        ],
    }

    wd_data = [None]
    for week in range(1):
        wd_data[week] = {
            "scenario": "n035w4",
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
                },
                {
                    "shiftType": "Early",
                    "skill": "Nurse",
                    "requirementOnMonday": {"minimum": 1, "optimal": 1},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 1},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                    "requirementOnThursday": {"minimum": 1, "optimal": 1},
                    "requirementOnFriday": {"minimum": 1, "optimal": 1},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 1, "optimal": 1},
                },
                {
                    "shiftType": "Early",
                    "skill": "Caretaker",
                    "requirementOnMonday": {"minimum": 2, "optimal": 2},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 2},
                    "requirementOnWednesday": {"minimum": 2, "optimal": 2},
                    "requirementOnThursday": {"minimum": 1, "optimal": 3},
                    "requirementOnFriday": {"minimum": 2, "optimal": 4},
                    "requirementOnSaturday": {"minimum": 0, "optimal": 1},
                    "requirementOnSunday": {"minimum": 1, "optimal": 2},
                },
                {
                    "shiftType": "Early",
                    "skill": "Trainee",
                    "requirementOnMonday": {"minimum": 1, "optimal": 2},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 1},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                    "requirementOnThursday": {"minimum": 0, "optimal": 0},
                    "requirementOnFriday": {"minimum": 1, "optimal": 1},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 0, "optimal": 0},
                },
                {
                    "shiftType": "Day",
                    "skill": "HeadNurse",
                    "requirementOnMonday": {"minimum": 0, "optimal": 0},
                    "requirementOnTuesday": {"minimum": 0, "optimal": 0},
                    "requirementOnWednesday": {"minimum": 0, "optimal": 0},
                    "requirementOnThursday": {"minimum": 0, "optimal": 0},
                    "requirementOnFriday": {"minimum": 0, "optimal": 0},
                    "requirementOnSaturday": {"minimum": 0, "optimal": 0},
                    "requirementOnSunday": {"minimum": 0, "optimal": 0},
                },
                {
                    "shiftType": "Day",
                    "skill": "Nurse",
                    "requirementOnMonday": {"minimum": 1, "optimal": 2},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 1},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                    "requirementOnThursday": {"minimum": 1, "optimal": 1},
                    "requirementOnFriday": {"minimum": 1, "optimal": 2},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 1, "optimal": 1},
                },
                {
                    "shiftType": "Day",
                    "skill": "Caretaker",
                    "requirementOnMonday": {"minimum": 2, "optimal": 2},
                    "requirementOnTuesday": {"minimum": 2, "optimal": 2},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 3},
                    "requirementOnThursday": {"minimum": 2, "optimal": 3},
                    "requirementOnFriday": {"minimum": 3, "optimal": 3},
                    "requirementOnSaturday": {"minimum": 0, "optimal": 0},
                    "requirementOnSunday": {"minimum": 1, "optimal": 2},
                },
                {
                    "shiftType": "Day",
                    "skill": "Trainee",
                    "requirementOnMonday": {"minimum": 1, "optimal": 2},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 1},
                    "requirementOnWednesday": {"minimum": 0, "optimal": 1},
                    "requirementOnThursday": {"minimum": 0, "optimal": 1},
                    "requirementOnFriday": {"minimum": 1, "optimal": 1},
                    "requirementOnSaturday": {"minimum": 0, "optimal": 0},
                    "requirementOnSunday": {"minimum": 0, "optimal": 0},
                },
                {
                    "shiftType": "Late",
                    "skill": "HeadNurse",
                    "requirementOnMonday": {"minimum": 0, "optimal": 0},
                    "requirementOnTuesday": {"minimum": 0, "optimal": 0},
                    "requirementOnWednesday": {"minimum": 0, "optimal": 0},
                    "requirementOnThursday": {"minimum": 1, "optimal": 1},
                    "requirementOnFriday": {"minimum": 0, "optimal": 0},
                    "requirementOnSaturday": {"minimum": 0, "optimal": 0},
                    "requirementOnSunday": {"minimum": 1, "optimal": 1},
                },
                {
                    "shiftType": "Late",
                    "skill": "Nurse",
                    "requirementOnMonday": {"minimum": 1, "optimal": 2},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 1},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                    "requirementOnThursday": {"minimum": 1, "optimal": 2},
                    "requirementOnFriday": {"minimum": 1, "optimal": 1},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 1, "optimal": 1},
                },
                {
                    "shiftType": "Late",
                    "skill": "Caretaker",
                    "requirementOnMonday": {"minimum": 2, "optimal": 2},
                    "requirementOnTuesday": {"minimum": 2, "optimal": 2},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 3},
                    "requirementOnThursday": {"minimum": 2, "optimal": 3},
                    "requirementOnFriday": {"minimum": 1, "optimal": 3},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 0, "optimal": 0},
                },
                {
                    "shiftType": "Late",
                    "skill": "Trainee",
                    "requirementOnMonday": {"minimum": 0, "optimal": 0},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 2},
                    "requirementOnWednesday": {"minimum": 0, "optimal": 0},
                    "requirementOnThursday": {"minimum": 1, "optimal": 1},
                    "requirementOnFriday": {"minimum": 0, "optimal": 1},
                    "requirementOnSaturday": {"minimum": 0, "optimal": 0},
                    "requirementOnSunday": {"minimum": 1, "optimal": 1},
                },
                {
                    "shiftType": "Night",
                    "skill": "HeadNurse",
                    "requirementOnMonday": {"minimum": 1, "optimal": 1},
                    "requirementOnTuesday": {"minimum": 0, "optimal": 0},
                    "requirementOnWednesday": {"minimum": 0, "optimal": 0},
                    "requirementOnThursday": {"minimum": 0, "optimal": 0},
                    "requirementOnFriday": {"minimum": 0, "optimal": 0},
                    "requirementOnSaturday": {"minimum": 0, "optimal": 0},
                    "requirementOnSunday": {"minimum": 0, "optimal": 0},
                },
                {
                    "shiftType": "Night",
                    "skill": "Nurse",
                    "requirementOnMonday": {"minimum": 1, "optimal": 1},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 2},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 2},
                    "requirementOnThursday": {"minimum": 1, "optimal": 1},
                    "requirementOnFriday": {"minimum": 1, "optimal": 1},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 1, "optimal": 1},
                },
                {
                    "shiftType": "Night",
                    "skill": "Caretaker",
                    "requirementOnMonday": {"minimum": 2, "optimal": 4},
                    "requirementOnTuesday": {"minimum": 2, "optimal": 3},
                    "requirementOnWednesday": {"minimum": 2, "optimal": 3},
                    "requirementOnThursday": {"minimum": 2, "optimal": 4},
                    "requirementOnFriday": {"minimum": 1, "optimal": 3},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 1, "optimal": 2},
                },
                {
                    "shiftType": "Night",
                    "skill": "Trainee",
                    "requirementOnMonday": {"minimum": 1, "optimal": 1},
                    "requirementOnTuesday": {"minimum": 1, "optimal": 2},
                    "requirementOnWednesday": {"minimum": 1, "optimal": 1},
                    "requirementOnThursday": {"minimum": 1, "optimal": 1},
                    "requirementOnFriday": {"minimum": 0, "optimal": 0},
                    "requirementOnSaturday": {"minimum": 1, "optimal": 1},
                    "requirementOnSunday": {"minimum": 1, "optimal": 1},
                },
            ],
            "shiftOffRequests": [],
            "vacations": [],
        }

    # initialize data
    num_nurses = 1
    num_shifts = len(sc_data["shiftTypes"])
    num_skills = len(sc_data["skills"])
    num_days = 7
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_skills = range(num_skills)
    all_weeks = range(1)

    data = {}
    data["configuration"] = config_data
    data["h0_data"] = h0_data
    data["h0_data_original"] = copy.deepcopy(h0_data)
    data["sc_data"] = sc_data
    data["wd_data"] = wd_data[0]
    data["all_wd_data"] = wd_data
    data["num_nurses"] = num_nurses
    data["num_shifts"] = num_shifts
    data["num_skills"] = num_skills
    data["num_days"] = num_days
    data["num_weeks"] = 1
    data["all_nurses"] = all_nurses
    data["all_shifts"] = all_shifts
    data["all_days"] = all_days
    data["all_skills"] = all_skills
    data["all_weeks"] = all_weeks

    return data


@pytest.fixture
def empty_results_1nurse_1week(data_for_1_nurse):
    num_days = data_for_1_nurse["num_days"]
    num_nurses = data_for_1_nurse["num_nurses"]
    num_skills = data_for_1_nurse["num_skills"]
    num_shifts = data_for_1_nurse["num_shifts"]
    week_number = 0

    results = {}

    for n in range(num_nurses):
        for d in range(num_days):
            for s in range(num_shifts):
                for sk in range(num_skills):
                    results[(n, d + 7 * week_number, s, sk)] = 0

    return results


@pytest.fixture
def results_1nurse_1full_week(data_for_1_nurse, empty_results_1nurse_1week):
    num_days = data_for_1_nurse["num_days"]
    results = empty_results_1nurse_1week
    for d in range(num_days):
        results[(0, d, 0, 0)] = 1
    return results


@pytest.fixture
def validator_for_1nurse_1week(data_for_1_nurse, empty_results_1nurse_1week):
    validator = ScheduleValidator()
    validator._init_variables(empty_results_1nurse_1week, data_for_1_nurse)
    return validator


class Schedule_modifier():
    @staticmethod
    def add_shifts(schedule, shift, skill, placement, number_of_shifts):
        if placement == utils.Shift_placement.START:
            for i in range(number_of_shifts):
                if i > 6:
                    break
                schedule[(0, i, shift, skill)] = 1
        if placement == utils.Shift_placement.MID:
            for i in range(number_of_shifts):
                if i > 6:
                    break
                schedule[(0, 1 + i, shift, skill)] = 1
        if placement == utils.Shift_placement.END:
            for i in range(number_of_shifts):
                if i < 0:
                    break
                schedule[(0, 6 - i, shift, skill)] = 1

    @staticmethod
    def remove_shifts(schedule, shift, skill, placement, number_of_shifts):
        if placement == utils.Shift_placement.START:
            for i in range(number_of_shifts):
                if i > 6:
                    break
                schedule[(0, i, shift, skill)] = 0
        if placement == utils.Shift_placement.MID:
            for i in range(number_of_shifts):
                if i > 6:
                    break
                schedule[(0, 1 + i, shift, skill)] = 0
        if placement == utils.Shift_placement.END:
            for i in range(number_of_shifts):
                if i < 0:
                    break
                schedule[(0, 6 - i, shift, skill)] = 0


@pytest.fixture
def schedule_modifier():
    return Schedule_modifier


@pytest.fixture
def all_false_config_data():
    return {
        "h1": False,
        "h2": False,
        "h3": False,
        "h4": False,
        "h5": False,
        "h6": False,
        "h7": False,
        "h8": False,
        "h9": False,
        "h10": False,
        "h11": False,
        "h12": False,
        "s1": False,
        "s2": False,
        "s3": False,
        "s4": False,
        "s5": False,
        "s6": False,
        "s7": False,
        "s8": False,
        "s9": False,
    }


class data_generator():
    @staticmethod
    def get_data(history_file_id, week_ids):

        data = {}

        data_generator.add_configuration_data(data)
        data_generator.add_history_data(data, history_file_id)
        data_generator.add_scenario_data(data, week_ids)
        data_generator.add_weeks_data(data, week_ids)

        return data

    @staticmethod
    def add_configuration_data(data):
        with open("test_data\\C0.json", "r") as file:
            config_data = json.load(file)
        data["configuration"] = config_data

    @staticmethod
    def add_history_data(data, history_file_id):

        with open(f"test_data\\H0-n035w4-{history_file_id}.json", "r") as file:
            history_data = json.load(file)

        data["h0_data"] = history_data
        data["h0_data_original"] = copy.deepcopy(history_data)

    @staticmethod
    def add_scenario_data(data, week_ids):

        with open("test_data\\Sc-n035w4.json", "r") as file:
            scenario_data = json.load(file)

        num_nurses = len(scenario_data["nurses"])
        num_shifts = len(scenario_data["shiftTypes"])
        num_skills = len(scenario_data["skills"])
        num_days = 7
        all_nurses = range(num_nurses)
        all_shifts = range(num_shifts)
        all_days = range(num_days)
        all_skills = range(num_skills)
        all_weeks = range(len(week_ids))
        data["sc_data"] = scenario_data
        data["num_nurses"] = num_nurses
        data["num_shifts"] = num_shifts
        data["num_skills"] = num_skills
        data["num_days"] = num_days
        data["num_weeks"] = len(week_ids)
        data["all_nurses"] = all_nurses
        data["all_shifts"] = all_shifts
        data["all_days"] = all_days
        data["all_skills"] = all_skills
        data["all_weeks"] = all_weeks

    @staticmethod
    def add_weeks_data(data, week_ids):

        weeks_data = []
        for week_id in week_ids:
            with open(f"test_data\\WD-n035w4-{week_id}.json", "r") as file:
                weeks_data.append(json.load(file))

        data["all_wd_data"] = weeks_data
        data["wd_data"] = weeks_data[0]


@pytest.fixture
def integration_tests_data_generator():
    return data_generator
