from nsp_solver.utils import utils


class HistorySimulator:

    def __init__(self):
        return

    def update_history_for_next_week(self, results, constants, week_number):
        constants["h0_data"]["week"] += 1
        working_days, shifts = self.compute_helpful_values(results, constants, week_number)

        self.update_border_data(constants, working_days, shifts)
        self.update_cumulative_data(constants, working_days, shifts)
        # print(history_data["nurseHistory"])

    def update_border_data(self, constants, working_days, shifts):
        for n in range(constants["num_nurses"]):
            if working_days[n][6] == 0:
                consecutive_free_days = 1
                d = 5
                while d >= 0 and working_days[n][d] == 0:
                    consecutive_free_days += 1
                    d -= 1
                constants["h0_data"]["nurseHistory"][n][
                    "numberOfConsecutiveDaysOff"
                ] = consecutive_free_days
                constants["h0_data"]["nurseHistory"][n]["numberOfConsecutiveWorkingDays"] = 0
                constants["h0_data"]["nurseHistory"][n]["numberOfConsecutiveAssignments"] = 0
                constants["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"] = "None"
            else:
                consecutive_work_days = 1
                d = 5
                while d >= 0 and working_days[n][d] == 1:
                    consecutive_work_days += 1
                    d -= 1
                constants["h0_data"]["nurseHistory"][n][
                    "numberOfConsecutiveWorkingDays"
                ] = consecutive_work_days
                constants["h0_data"]["nurseHistory"][n]["numberOfConsecutiveDaysOff"] = 0

                consecutive_shift = 0
                for s in range(constants["num_shifts"]):
                    if shifts[n][6][s] == 1:
                        consecutive_shift = s
                consecutive_shifts = 1
                for shift_name, shift_id in utils.shift_to_int.items():
                    if shift_id == consecutive_shift:
                        constants["h0_data"]["nurseHistory"][n][
                            "lastAssignedShiftType"
                        ] = shift_name

                d = 5
                while d >= 0 and shifts[n][d][consecutive_shift] == 1:
                    consecutive_shifts += 1
                    d -= 1
                constants["h0_data"]["nurseHistory"][n][
                    "numberOfConsecutiveAssignments"
                ] = consecutive_shifts

    def update_cumulative_data(self, constants, working_days, shifts):
        for n in range(constants["num_nurses"]):
            for d in range(constants["num_days"]):
                for s in range(constants["num_shifts"]):
                    constants["h0_data"]["nurseHistory"][n]["numberOfAssignments"] += shifts[n][d][s]

            weekend_working_days = sum(working_days[n][5:7])
            constants["h0_data"]["nurseHistory"][n]["numberOfWorkingWeekends"] += self.isPositiveNumber(weekend_working_days)
            if weekend_working_days == 1:
                constants["h0_data"]["nurseHistory"][n]["numberOfIncompleteWeekends"] += weekend_working_days

    def compute_helpful_values(self, results, constants, week_number):
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
                    if shifts[n][d][s] == 1:
                        working_days[n][d] = 1

        constants["wd_data"]["vacations_with_ids"] = list(
            map(lambda x: int(x.split("_")[1]), constants["wd_data"]["vacations"])
        )

        return working_days, shifts

    def isPositiveNumber(self, number):
        if number > 0:
            return 1
        return 0
