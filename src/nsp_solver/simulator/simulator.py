from nsp_solver.utils import utils


def update_history_for_next_week(results, constants, week_number):
    num_days = constants["num_days"]
    num_nurses = constants["num_nurses"]
    num_skills = constants["num_skills"]
    num_shifts = constants["num_shifts"]
    history_data = constants["h0_data"]

    working_days, shifts = compute_helpful_values(results, constants, week_number)
    
    for n in range(num_nurses):
        for d in range(num_days):
            history_data["nurseHistory"][n]["numberOfAssignments"] += working_days[n][d]
            
        history_data["nurseHistory"][n]["numberOfWorkingWeekends"] += isPositiveNumber(sum(working_days[n][5:7]))

        if working_days[n][6] == 0:
            consecutive_free_days = 1
            d = 5
            while d >= 0 and working_days[n][d] == 0:
                consecutive_free_days += 1
                d -= 1
            history_data["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ] = consecutive_free_days
            history_data["nurseHistory"][n]["numberOfConsecutiveWorkingDays"] = 0
            history_data["nurseHistory"][n]["numberOfConsecutiveAssignments"] = 0
            history_data["nurseHistory"][n]["lastAssignedShiftType"] = "None"
        else:
            consecutive_work_days = 1
            d = 5
            while d >= 0 and working_days[n][d] == 1:
                consecutive_work_days += 1
                d -= 1
            history_data["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ] = consecutive_work_days
            history_data["nurseHistory"][n]["numberOfConsecutiveDaysOff"] = 0

            consecutive_shift = 0
            for s in range(num_shifts):
                if shifts[n][6][s] == 1:
                    consecutive_shift = s
                    break
            consecutive_shifts = 1
            for shift_name, shift_id in utils.get_shift_to_int().items():
                if shift_id == consecutive_shift:
                    history_data["nurseHistory"][n][
                        "lastAssignedShiftType"
                    ] = shift_name

            d = 5
            while d >= 0 and shifts[n][d][consecutive_shift] == 1:
                consecutive_shifts += 1
                d -= 1
            history_data["nurseHistory"][n][
                "numberOfConsecutiveAssignments"
            ] = consecutive_shifts
    print(history_data["nurseHistory"])

def compute_helpful_values(results, constants, week_number):
    num_days = constants["num_days"]
    num_nurses = constants["num_nurses"]
    num_skills = constants["num_skills"]
    num_shifts = constants["num_shifts"]
    working_days = [[0 for _ in range(num_days)] for _ in range(num_nurses)]
    shifts = [[[0 for _ in range(num_shifts)] for _ in range(num_days)] for _ in range(num_nurses)]

    for n in range(num_nurses):
        for d in range(num_days):
            for s in range(num_shifts):
                shifts[n][d][s] = sum(results[(n, d + 7 * week_number, s, sk)] for sk in range(num_skills))
            working_days[n][d] = sum(shifts[n][d][:])
    
    return working_days, shifts

def isPositiveNumber(number):
    if number > 0: return 1
    return 0