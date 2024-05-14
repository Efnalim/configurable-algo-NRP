shift_to_int = {"Early": 0, "Day": 1, "Late": 2, "Night": 3, "Any": 4, "None": 5}
skill_to_int = {"HeadNurse": 0, "Nurse": 1, "Caretaker": 2, "Trainee": 3}
contract_to_int = {"FullTime": 0, "PartTime": 1, "HalfTime": 2}
day_to_int = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
OPT_CAPACITY_WEIGHT = 30
CONS_WORK_DAY_WEIGHT = 30
CONS_SHIFT_WEIGHT = 15
CONS_DAY_OFF_WEIGHT = 30
UNSATISFIED_PREFERENCE_WEIGHT = 10
INCOMPLETE_WEEKEDN_WEIGHT = 30
CONS_WORK_DAY_WEIGHT = 30
TOTAL_ASSIGNMENTS_WEIGHT = 20
TOTAL_WORKING_WEEKENDS_WEIGHT = 30

def isPositiveNumber(number):
    if number > 0: return 1
    return 0
