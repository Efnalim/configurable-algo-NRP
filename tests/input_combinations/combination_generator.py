from allpairspy import AllPairs
from collections import OrderedDict

from nsp_solver.utils import utils

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

print("----------------------------------------------------------------")
print("----------------------------------------------------------------")

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

print("----------------------------------------------------------------")
print("----------------------------------------------------------------")

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

print("----------------------------------------------------------------")
print("----------------------------------------------------------------")
