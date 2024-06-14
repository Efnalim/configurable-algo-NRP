from allpairspy import AllPairs
from collections import OrderedDict

from colorama import Fore, init
from nsp_solver.utils import utils

init(autoreset=True)

parameters = OrderedDict({
    "maximumNumberOfConsecutiveDaysOff": [5],
    "numberOfConsecutiveDaysOffPrevWeek": [0, 1, 5, 6],
    "numberOfConsecutiveDaysOffThisWeek": [0, 1, 5, 6],
    "placement": [utils.Shift_placement.START, utils.Shift_placement.MID, utils.Shift_placement.END],
})

print("test_get_max_consecutive_days_off_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")

parameters = OrderedDict({
    "maximumNumberOfConsecutiveDaysOff": [2],
    "numberOfConsecutiveDaysOffPrevWeek": [0, 1, 2],
    "numberOfConsecutiveDaysOffThisWeek": [0, 1, 2],
    "placement": [utils.Shift_placement.START, utils.Shift_placement.MID, utils.Shift_placement.END],
})

print("test_get_min_consecutive_days_off_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")

parameters = OrderedDict({
    "number_of_preferences": [0, 1, 2],
    "number_of_preferences_satisfied": [0, 1, 2],
    "preferences_type": ["shift", "whole_day"],
})


def is_valid_preference_combination(row):
    if len(row) >= 2:
        return row[1] <= row[0]
    return True


print("test_get_assignment_preferences_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters, filter_func=is_valid_preference_combination)):
    # for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")

parameters = OrderedDict({
    "complete_weekends": [False, True],
    "working": ["none", "saturday", "sunday", "saturday and sunday"],
})

print("test_get_incomplete_weekends_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters)):
    # for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")

parameters = OrderedDict({
    "working_days": ["n_under_min", "1_under_min", "exactly_min", "exactly_max", "1_over_max", "n_over_max"],
    "limits": ["min_2__max_4"]
})

print("test_get_total_assignments_out_of_limits_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters)):
    # for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")

parameters = OrderedDict({
    "working_days": ["none", "saturday only", "sunday only", "saturday and sunday"],
    "max_total_weekends": [0, 1]
})

print("test_get_total_weekends_over_limit_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters)):
    # for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")

parameters = OrderedDict({
    "working_days_skills": ["none", "all_skills"],
    "ifneeded_skills": ["None", "few"]
})

print("test_get_total_uses_of_ifneeded_skills_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters)):
    # for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")

parameters = OrderedDict({
    "max_assignments": [4],
    "overtime_wanted": [0, 2],
    "number_of_assignments": [0, 4, 5, 6, 7],
})

print("test_get_unsatisfied_overtime_preferences_value")
print("----------------------------------------------------------------")
for i, pairs in enumerate(AllPairs(parameters)):
    print("{:2d}: {}".format(i, pairs))

print(Fore.MAGENTA + "================================================================")
