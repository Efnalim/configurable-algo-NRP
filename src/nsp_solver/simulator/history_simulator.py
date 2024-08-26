from nsp_solver.utils import utils


class HistorySimulator:

    def update_history_for_next_week(self, results, data):
        week_number = data["h0_data"]["week"]
        data["h0_data"]["week"] += 1
        working_days, shifts = self._compute_helpful_values(results, data, week_number)

        self._update_border_data(data, working_days, shifts)
        self._update_cumulative_data(data, working_days, shifts)
        # print(history_data["nurseHistory"])

    def _update_border_data(self, data, working_days, shifts):
        for n in range(data["num_nurses"]):
            if working_days[n][6] == 0:
                consecutive_free_days = 1
                d = 5
                while d >= 0 and working_days[n][d] == 0:
                    consecutive_free_days += 1
                    d -= 1
                data["h0_data"]["nurseHistory"][n][
                    "numberOfConsecutiveDaysOff"
                ] = consecutive_free_days
                data["h0_data"]["nurseHistory"][n]["numberOfConsecutiveWorkingDays"] = 0
                data["h0_data"]["nurseHistory"][n]["numberOfConsecutiveAssignments"] = 0
                data["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"] = "None"
            else:
                consecutive_work_days = 1
                d = 5
                while d >= 0 and working_days[n][d] == 1:
                    consecutive_work_days += 1
                    d -= 1
                data["h0_data"]["nurseHistory"][n][
                    "numberOfConsecutiveWorkingDays"
                ] = consecutive_work_days
                data["h0_data"]["nurseHistory"][n]["numberOfConsecutiveDaysOff"] = 0

                consecutive_shift = 0
                for s in range(data["num_shifts"]):
                    if shifts[n][6][s] == 1:
                        consecutive_shift = s
                consecutive_shifts = 1
                for shift_name, shift_id in utils.shift_to_int.items():
                    if shift_id == consecutive_shift:
                        data["h0_data"]["nurseHistory"][n][
                            "lastAssignedShiftType"
                        ] = shift_name

                d = 5
                while d >= 0 and shifts[n][d][consecutive_shift] == 1:
                    consecutive_shifts += 1
                    d -= 1
                data["h0_data"]["nurseHistory"][n][
                    "numberOfConsecutiveAssignments"
                ] = consecutive_shifts

    def _update_cumulative_data(self, data, working_days, shifts):
        for n in range(data["num_nurses"]):
            for d in range(data["num_days"]):
                for s in range(data["num_shifts"]):
                    data["h0_data"]["nurseHistory"][n]["numberOfAssignments"] += shifts[n][d][s]

            weekend_working_days = sum(working_days[n][5:7])
            data["h0_data"]["nurseHistory"][n]["numberOfWorkingWeekends"] += self.__isPositiveNumber(weekend_working_days)
            if weekend_working_days == 1:
                data["h0_data"]["nurseHistory"][n]["numberOfIncompleteWeekends"] += weekend_working_days

    def _compute_helpful_values(self, results, data, week_number):
        num_days = data["num_days"]
        num_nurses = data["num_nurses"]
        num_skills = data["num_skills"]
        num_shifts = data["num_shifts"]
        working_days = [[0 for _ in range(num_days)] for _ in range(num_nurses)]
        shifts = [[[0 for _ in range(num_shifts)] for _ in range(num_days)] for _ in range(num_nurses)]

        for n in range(num_nurses):
            for d in range(num_days):
                for s in range(num_shifts):
                    shifts[n][d][s] = sum(results[(n, d + 7 * week_number, s, sk)] for sk in range(num_skills))
                    if shifts[n][d][s] == 1:
                        working_days[n][d] = 1

        data["wd_data"]["vacations_with_ids"] = list(
            map(lambda x: int(x.split("_")[1]), data["wd_data"]["vacations"])
        )

        return working_days, shifts

    def __isPositiveNumber(self, number):
        if number > 0:
            return 1
        return 0
