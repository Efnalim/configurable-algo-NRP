import math
from nsp_solver.utils import utils


class ScheduleValidator:
    def __init__(self, schedule, constants, config, num_week):
        self.schedule = schedule
        self.constants = constants
        self.config = config
        self.num_week = num_week
        self.help_vars = self.compute_helpful_values()

    def is_schedule_valid(self) -> bool:
        print("checking validity of schedule")

        if self.is_minimal_capacity_satisfied() is False:
            print("is_minimal_capacity_satisfied returns False")
            return False

        if self.is_max_assignments_per_day_satisfied() is False:
            print("is_max_assignments_per_day_satisfied returns False")
            return False

        if self.is_required_skill_satisfied() is False:
            print("is_required_skill_satisfied returns False")
            return False

        if self.is_shift_successsion_satisfied() is False:
            print("is_shift_successsion_satisfied returns False")
            return False

        return True

    def get_objective_value_of_schedule(self) -> int:
        print("computing optimality of schedule")
        total = 0
        total += self.get_optimal_capacity_value()
        total += self.get_consecutive_assignments_value()
        total += self.get_consecutive_days_off_value()
        total += self.get_assignment_preferences_value()
        total += self.get_incomplete_weekends_value()
        return total

    def is_minimal_capacity_satisfied(self) -> bool:
        requirements = self.constants["wd_data"]["requirements"]

        for req in requirements:
            all_nurses = self.constants["all_nurses"]

            s = utils.shift_to_int[req["shiftType"]]
            sk = utils.skill_to_int[req["skill"]]
            minimal_capacities_in_week = [
                req["requirementOnMonday"]["minimum"],
                req["requirementOnTuesday"]["minimum"],
                req["requirementOnWednesday"]["minimum"],
                req["requirementOnThursday"]["minimum"],
                req["requirementOnFriday"]["minimum"],
                req["requirementOnSaturday"]["minimum"],
                req["requirementOnSunday"]["minimum"],
            ]

            for d, min_capacity in enumerate(minimal_capacities_in_week):
                skills_worked = [
                    self.help_vars["shifts_and_skills"][n][d][s][sk] for n in all_nurses
                ]
                if min_capacity > sum(skills_worked):
                    return False

        return True

    def is_max_assignments_per_day_satisfied(self) -> bool:
        all_nurses = self.constants["all_nurses"]
        all_days = self.constants["all_days"]

        for n in all_nurses:
            for d in all_days:
                if sum(self.help_vars["shifts"][n][d][:]) > 1:
                    return False

        return True

    def is_required_skill_satisfied(self) -> bool:
        nurses_data = self.constants["sc_data"]["nurses"]
        all_skills = self.constants["all_skills"]
        all_days = self.constants["all_days"]
        all_shifts = self.constants["all_shifts"]

        for n, nurse_data in enumerate(nurses_data):
            for sk in all_skills:
                has_skill = False
                for skill in nurse_data["skills"]:
                    if sk == utils.skill_to_int[skill]:
                        has_skill = True
                        break
                if has_skill is False:
                    for d in all_days:
                        for s in all_shifts:
                            if self.help_vars["shifts_and_skills"][n][d][s][sk] > 0:
                                return False
        return True

    def is_shift_successsion_satisfied(self) -> bool:
        restrictions = self.constants["sc_data"]["forbiddenShiftTypeSuccessions"]
        all_nurses = self.constants["all_nurses"]
        num_days = self.constants["num_days"]
        all_shifts = self.constants["all_shifts"]

        shifts = self.help_vars["shifts"]

        for n in all_nurses:
            for d in range(num_days - 1):
                for s in all_shifts:
                    if restrictions[s]["succeedingShiftTypes"] == []:
                        break
                    if shifts[n][d][s] == 0:
                        break
                    for forbidden_shift_succession in restrictions[s][
                        "succeedingShiftTypes"
                    ]:
                        if (
                            shifts[n][d + 1][
                                utils.shift_to_int[forbidden_shift_succession]
                            ]
                            == 1
                        ):
                            return False
            last_shift = utils.shift_to_int[
                self.constants["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]
            if last_shift == utils.shift_to_int["None"]:
                break
            if restrictions[last_shift]["succeedingShiftTypes"] == []:
                break
            for forbidden_shift_succession in restrictions[last_shift][
                "succeedingShiftTypes"
            ]:
                if shifts[n][0][utils.shift_to_int[forbidden_shift_succession]] == 1:
                    return False

        return True

    def compute_helpful_values(self):
        num_days = self.constants["num_days"]
        num_nurses = self.constants["num_nurses"]
        num_skills = self.constants["num_skills"]
        num_shifts = self.constants["num_shifts"]
        working_days = [[0 for _ in range(num_days)] for _ in range(num_nurses)]
        shifts = [
            [[0 for _ in range(num_shifts)] for _ in range(num_days)]
            for _ in range(num_nurses)
        ]
        shifts_and_skills = [
            [
                [[0 for _ in range(num_skills)] for _ in range(num_shifts)]
                for _ in range(num_days)
            ]
            for _ in range(num_nurses)
        ]

        for n in range(num_nurses):
            for d in range(num_days):
                for s in range(num_shifts):
                    for sk in range(num_skills):
                        shifts_and_skills[n][d][s][sk] = self.schedule[
                            (n, d + 7 * self.num_week, s, sk)
                        ]
                    shifts[n][d][s] = sum(
                        self.schedule[(n, d + 7 * self.num_week, s, sk)]
                        for sk in range(num_skills)
                    )
                working_days[n][d] = sum(shifts[n][d][:])

        ret_val = {}
        ret_val["working_days"] = working_days
        ret_val["shifts"] = shifts
        ret_val["shifts_and_skills"] = shifts_and_skills

        return ret_val

    def get_optimal_capacity_value(self) -> int:
        subtotal = 0
        requirements = self.constants["wd_data"]["requirements"]

        for req in requirements:
            all_nurses = self.constants["all_nurses"]

            s = utils.shift_to_int[req["shiftType"]]
            sk = utils.skill_to_int[req["skill"]]
            optimal_capacities_in_week = [
                req["requirementOnMonday"]["optimal"],
                req["requirementOnTuesday"]["optimal"],
                req["requirementOnWednesday"]["optimal"],
                req["requirementOnThursday"]["optimal"],
                req["requirementOnFriday"]["optimal"],
                req["requirementOnSaturday"]["optimal"],
                req["requirementOnSunday"]["optimal"],
            ]

            for d, opt_capacity in enumerate(optimal_capacities_in_week):
                skills_worked = [
                    self.help_vars["shifts_and_skills"][n][d][s][sk] for n in all_nurses
                ]
                diff = opt_capacity > sum(skills_worked)
                if diff > 0:
                    subtotal += diff * utils.OPT_CAPACITY_WEIGHT

        return subtotal

    def get_consecutive_assignments_value(self) -> int:
        subtotal = 0
        subtotal += self.get_max_consecutive_work_days_value()
        subtotal += self.get_max_consecutive_shifts_value()
        subtotal += self.get_min_consecutive_work_days_value()
        subtotal += self.get_min_consecutive_shifts_value()
        return subtotal

    def get_max_consecutive_work_days_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        all_days = self.constants["all_days"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_working_days_prev_week = self.constants["h0_data"][
                "nurseHistory"
            ][n]["numberOfConsecutiveWorkingDays"]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                if d > max_consecutive_working_days:
                    diff = (
                        sum(
                            self.help_vars["working_days"][n][
                                d - max_consecutive_working_days : d + 1
                            ]
                        )
                        - max_consecutive_working_days
                    )
                    if diff > 0:
                        subtotal += diff * utils.CONS_WORK_DAY_WEIGHT
                else:
                    if (
                        consecutive_working_days_prev_week
                        >= max_consecutive_working_days - d
                    ):
                        diff = sum(self.help_vars["working_days"][n][0 : d + 1]) - d
                        if diff > 0:
                            subtotal += diff * utils.CONS_WORK_DAY_WEIGHT

        return subtotal

    def get_max_consecutive_shifts_value(self) -> int:
        all_nurses = self.constants["all_nurses"]
        all_days = self.constants["all_days"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        subtotal = 0

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                self.constants["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]
            consecutive_shifts_prev_week = self.constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveAssignments"
            ]
            for s in all_shifts:
                max_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "maximumNumberOfConsecutiveAssignments"
                ]
                for d in all_days:
                    if d > max_consecutive_working_shifts:
                        diff = (
                            sum(
                                [
                                    self.help_vars["shifts"][n][d - dd][s]
                                    for dd in range(1 + max_consecutive_working_shifts)
                                ]
                            )
                            - max_consecutive_working_shifts
                        )
                        if diff > 0:
                            subtotal += diff * utils.CONS_SHIFT_WEIGHT
                    else:
                        if (last_shift == s) and (
                            consecutive_shifts_prev_week
                            >= max_consecutive_working_shifts - d
                        ):
                            diff = (
                                sum(
                                    [
                                        self.help_vars["shifts"][n][dd][s]
                                        for dd in range(d + 1)
                                    ]
                                )
                                - d
                            )
                            if diff > 0:
                                subtotal += diff * utils.CONS_SHIFT_WEIGHT
        return subtotal

    def get_min_consecutive_work_days_value(self) -> int:
        all_nurses = self.constants["all_nurses"]
        all_days = self.constants["all_days"]
        sc_data = self.constants["sc_data"]

        subtotal = 0

        for n in all_nurses:
            consecutive_working_days_prev_week = self.constants["h0_data"][
                "nurseHistory"
            ][n]["numberOfConsecutiveWorkingDays"]
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    if (d - dd) > 0:
                        diff = (
                            (1 - self.help_vars["working_days"][n][d])
                            + sum(self.help_vars["working_days"][n][d - dd : d])
                            + (1 - self.help_vars["working_days"][n][d - dd - 1])
                            - (dd + 1)
                        )
                        if diff > 0:
                            subtotal += diff * utils.CONS_WORK_DAY_WEIGHT * dd

                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            diff = (
                                (1 - self.help_vars["working_days"][n][d])
                                + sum(self.help_vars["working_days"][n][0:d])
                                - d
                            )
                            if diff > 0:
                                subtotal += diff * utils.CONS_WORK_DAY_WEIGHT * dd
        return subtotal

    def get_min_consecutive_shifts_value(self) -> int:
        subtotal = 0

        all_nurses = self.constants["all_nurses"]
        all_days = self.constants["all_days"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_working_shifts_prev_week = self.constants["h0_data"][
                "nurseHistory"
            ][n]["numberOfConsecutiveWorkingDays"]
            lastAssignedShiftType = self.constants["h0_data"]["nurseHistory"][n][
                "lastAssignedShiftType"
            ]
            lastShittTypeAsInt = utils.shift_to_int[lastAssignedShiftType]
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignments"
                    ]
                    for dd in range(1, min_consecutive_shifts):
                        if (d - dd) > 0:
                            diff = (
                                (1 - self.help_vars["shifts"][n][d][s])
                                + sum(
                                    [
                                        self.help_vars["shifts"][n][ddd][s]
                                        for ddd in range(d - dd, d)
                                    ]
                                )
                                + (1 - self.help_vars["shifts"][n][d - dd - 1][s])
                                - (dd + 1)
                            )
                            if diff > 0:
                                subtotal += diff * utils.CONS_SHIFT_WEIGHT * dd
                        else:
                            if (consecutive_working_shifts_prev_week == d - dd) and (
                                lastShittTypeAsInt == s
                            ):
                                diff = (1 - self.help_vars["shifts"][n][d][s]) + sum(
                                    [
                                        self.help_vars["shifts"][n][ddd][s]
                                        for ddd in range(d) - d
                                    ]
                                )
                                if diff > 0:
                                    subtotal += diff * utils.CONS_SHIFT_WEIGHT * dd
        return subtotal

    def get_consecutive_days_off_value(self) -> int:
        subtotal = 0
        subtotal += self.get_max_consecutive_days_off_value()
        subtotal += self.get_min_consecutive_days_off_value()
        return subtotal

    def get_max_consecutive_days_off_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        all_days = self.constants["all_days"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_days_off_prev_week = self.constants["h0_data"]["nurseHistory"][
                n
            ]["numberOfConsecutiveDaysOff"]
            max_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                if d > max_consecutive_days_off:
                    if (
                        sum(
                            self.help_vars["working_days"][n][
                                d - max_consecutive_days_off : d + 1
                            ]
                        )
                        == 0
                    ):
                        subtotal += utils.CONS_DAY_OFF_WEIGHT
                else:
                    if consecutive_days_off_prev_week >= max_consecutive_days_off - d:
                        if sum(self.help_vars["working_days"][n][0 : d + 1]) == 0:
                            subtotal += utils.CONS_DAY_OFF_WEIGHT
        return subtotal

    def get_min_consecutive_days_off_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        all_days = self.constants["all_days"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_working_days_prev_week = self.constants["h0_data"][
                "nurseHistory"
            ][n]["numberOfConsecutiveDaysOff"]
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    if (d - dd) > 0:
                        diff = (
                            self.help_vars["working_days"][n][d]
                            + sum(
                                [
                                    (1 - self.help_vars["working_days"][n][ddd])
                                    for ddd in range(d - dd, d)
                                ]
                            )
                            + self.help_vars["working_days"][n][d - dd - 1]
                            - (dd + 1)
                        )
                        if diff > 0:
                            subtotal += diff * utils.CONS_DAY_OFF_WEIGHT * dd
                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            diff = (
                                self.help_vars["working_days"][n][d]
                                + sum(
                                    [
                                        (1 - self.help_vars["working_days"][n][ddd])
                                        for ddd in range(0, d)
                                    ]
                                )
                                - d
                            )
                            if diff > 0:
                                subtotal += diff * utils.CONS_DAY_OFF_WEIGHT * dd
        return subtotal

    def get_assignment_preferences_value(self) -> int:
        subtotal = 0
        for preference in self.constants["wd_data"]["shiftOffRequests"]:
            nurse_id = int(preference["nurse"].split("_")[1])
            day_id = utils.day_to_int[preference["day"]]
            shift_id = utils.shift_to_int[preference["shiftType"]]

            if shift_id != utils.shift_to_int["Any"]:
                if self.help_vars["shifts"][nurse_id][day_id][shift_id] == 1:
                    subtotal += utils.UNSATISFIED_PREFERENCE_WEIGHT
            else:
                if self.help_vars["working_days"][nurse_id][day_id] == 1:
                    subtotal += utils.UNSATISFIED_PREFERENCE_WEIGHT
        return subtotal

    def get_incomplete_weekends_value(self) -> int:
        subtotal = 0
        nurses_data = self.constants["sc_data"]["nurses"]
        contracts_data = self.constants["sc_data"]["contracts"]
        all_nurses = self.constants["all_nurses"]

        for n in all_nurses:
            isCompleteWeekendRequested = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["completeWeekends"]
            if isCompleteWeekendRequested == 1:
                if (
                    self.help_vars["working_days"][n][5]
                    + self.help_vars["working_days"][n][6]
                    == 1
                ):
                    subtotal += utils.INCOMPLETE_WEEKEDN_WEIGHT
        return subtotal

    def get_all_weeks_objective_value(self) -> int:
        total = 0
        total += self.get_all_weeks_max_min_assignments()
        total += self.get_all_weeks_max_working_weekends()
        return total

    def get_all_weeks_max_min_assignments(self) -> int:
        subtotal = 0
        nurses_data = self.constants["sc_data"]["nurses"]
        contracts_data = self.constants["sc_data"]["contracts"]
        all_nurses = self.constants["all_nurses"]
        num_days = self.constants["num_days"]
        num_weeks = self.constants["num_weeks"]
        all_shifts = self.constants["all_shifts"]
        all_skills = self.constants["all_skills"]

        for n in all_nurses:
            upper_limit = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["maximumNumberOfAssignments"]

            lower_limit = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["minimumNumberOfAssignments"]

            total_assignments = sum([self.schedule[(n, d, s, sk)] for d in range(num_days*num_weeks) for s in all_shifts for sk in all_skills])
            diff = total_assignments - upper_limit
            if diff > 0:
                subtotal += diff * utils.TOTAL_ASSIGNMENTS_WEIGHT
            diff = lower_limit - total_assignments
            if diff > 0:
                subtotal += diff * utils.TOTAL_ASSIGNMENTS_WEIGHT

        return subtotal

    def get_all_weeks_max_working_weekends(self) -> int:
        subtotal = 0
        sc_data = self.constants["sc_data"]
        all_nurses = self.constants["all_nurses"]
        num_weeks = self.constants["num_weeks"]
        all_shifts = self.constants["all_shifts"]
        all_skills = self.constants["all_skills"]

        for n in all_nurses:
            worked_weekends_limit = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfWorkingWeekends"]
            total_working_weekends = 0
            for w in range(num_weeks):
                if sum([self.schedule[(n, 5 + 7 * w, s, sk)] + self.schedule[(n, 6 + 7 * w, s, sk)] for s in all_shifts for sk in all_skills]) > 0:
                    total_working_weekends += 1
            diff = total_working_weekends - worked_weekends_limit
            if diff > 0:
                subtotal += diff * utils.TOTAL_WORKING_WEEKENDS_WEIGHT
        return subtotal
