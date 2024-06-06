import math
from nsp_solver.utils import utils


class ScheduleValidator:
    def __init__(self, schedule, constants):
        self.schedule = schedule
        self.constants = constants
        self.config = constants["configuration"]
        self.all_days = range(constants["num_days"] * constants["num_weeks"])
        self.help_vars = self.compute_helpful_values()

    def evaluate_results(self) -> int:
        if self.is_schedule_valid():
            return self.get_objective_value_of_schedule()
        else:
            return 99999

    def is_schedule_valid(self) -> bool:
        if self.config["h1"] and not self.is_max_assignments_per_day_satisfied():
            print("is_max_assignments_per_day_satisfied returns False")
            return False

        if self.config["h2"] and not self.is_minimal_capacity_satisfied():
            print("is_minimal_capacity_satisfied returns False")
            return False

        if self.config["h3"] and not self.is_shift_successsion_satisfied():
            print("is_shift_successsion_satisfied returns False")
            return False

        if self.config["h4"] and not self.is_required_skill_satisfied():
            print("is_required_skill_satisfied returns False")
            return False

        if (
            self.config["h5"]
            and not self.is_min_max_consecutive_assignments_satisfied()
        ):
            print("is_min_max_consecutive_assignments_satisfied returns False")
            return False

        if self.config["h6"] and not self.is_min_max_consecutive_days_off_satisfied():
            print("is_min_max_consecutive_days_off_satisfied returns False")
            return False

        if self.config["h7"] and not self.is_max_total_incomplete_weekends_satisfied():
            print("is_max_total_incomplete_weekends_satisfied returns False")
            return False

        if self.config["h8"] and not self.is_min_max_total_assignments_satisfied():
            print("is_min_max_total_assignments_satisfied returns False")
            return False

        if self.config["h9"] and not self.is_min_free_period_satisfied():
            print("is_min_free_period_satisfied returns False")
            return False

        if (
            self.config["h10"]
            and not self.is_max_assignments_per_day_with_exception_satisfied()
        ):
            print("is_max_assignments_per_day_with_exception returns False")
            return False

        if (
            self.config["h11"]
            and not self.is_maximum_shifts_of_specific_type_satisfied()
        ):
            print("is_maximum_shifts_of_specific_type_satisfied returns False")
            return False

        if self.config["h12"] and not self.is_planned_vacations_satisfied():
            print("is_planned_vacations_satisfied returns False")
            return False

        return True

    def get_objective_value_of_schedule(self) -> int:
        total = 0
        if self.config["s1"]:
            total += self.get_optimal_capacity_value()
        if self.config["s2"]:
            total += self.get_consecutive_assignments_value()
        if self.config["s3"]:
            total += self.get_consecutive_days_off_value()
        if self.config["s4"]:
            total += self.get_assignment_preferences_value()
        if self.config["s5"]:
            total += self.get_incomplete_weekends_value()
        if self.config["s6"]:
            total += self.get_total_assignments_out_of_limits_value()
        if self.config["s7"]:
            total += self.get_total_weekends_over_limit_value()
        if self.config["s8"]:
            total += self.get_total_uses_of_ifneeded_skills_value()
        if self.config["s9"]:
            total += self.get_unsatisfied_overtime_preferences_value()
        return total

    def is_minimal_capacity_satisfied(self) -> bool:
        all_weeks = self.constants["all_weeks"]

        for w in all_weeks:
            requirements = self.constants["all_wd_data"][w]["requirements"]

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
                        self.help_vars["shifts_and_skills"][n][d + 7 * w][s][sk]
                        for n in all_nurses
                    ]
                    if min_capacity > sum(skills_worked):
                        return False

        return True

    def is_max_assignments_per_day_satisfied(self) -> bool:
        all_nurses = self.constants["all_nurses"]

        for n in all_nurses:
            for d in self.all_days:
                if sum(self.help_vars["shifts"][n][d][:]) > 1:
                    print(f"{n} {d}")
                    return False

        return True

    def is_max_assignments_per_day_with_exception_satisfied(self) -> bool:
        all_nurses = self.constants["all_nurses"]

        for n in all_nurses:
            for d in self.all_days:
                if (
                    sum(self.help_vars["shifts"][n][d][1:]) > 1
                    or sum(self.help_vars["shifts"][n][d][:-1]) > 1
                ):
                    print(f"{n} {d}")
                    return False

        return True

    def is_planned_vacations_satisfied(self) -> bool:
        all_weeks = self.constants["all_weeks"]

        for w in all_weeks:
            for n in self.help_vars["nurses_ids_on_vacation"][w]:
                if sum(self.help_vars["working_days"][n][w * 7: (w + 1) * 7]) > 0:
                    print(f"{n} {w}")
                    return False

        return True

    def is_maximum_shifts_of_specific_type_satisfied(self) -> bool:
        all_nurses = self.constants["all_nurses"]
        for n in all_nurses:
            for restriction in self.constants["sc_data"]["nurses"][n]["restrictions"]:
                shift_id = utils.shift_to_int[restriction["type"]]
                limit = restriction["limit"]
                if (
                    sum(self.help_vars["shifts"][n][d][shift_id] for d in self.all_days)
                    > limit
                ):
                    print(f"n{n} res_s{shift_id}")
                    return False

        return True

    def is_required_skill_satisfied(self) -> bool:
        nurses_data = self.constants["sc_data"]["nurses"]
        all_skills = self.constants["all_skills"]
        all_shifts = self.constants["all_shifts"]

        for n, nurse_data in enumerate(nurses_data):
            for sk in all_skills:
                has_skill = False
                for skill in nurse_data["skills"]:
                    if sk == utils.skill_to_int[skill]:
                        has_skill = True
                        break
                if has_skill is False:
                    for d in self.all_days:
                        for s in all_shifts:
                            if self.help_vars["shifts_and_skills"][n][d][s][sk] > 0:
                                return False
        return True

    def is_shift_successsion_satisfied(self) -> bool:
        restrictions = self.constants["sc_data"]["forbiddenShiftTypeSuccessions"]
        all_nurses = self.constants["all_nurses"]
        num_days = self.constants["num_days"] * self.constants["num_weeks"]
        all_shifts = self.constants["all_shifts"]

        shifts = self.help_vars["shifts"]

        for n in all_nurses:
            for d in range(num_days - 1):
                for s in all_shifts:
                    if restrictions[s]["succeedingShiftTypes"] == []:
                        continue
                    if shifts[n][d][s] == 0:
                        continue
                    for forbidden_shift_succession in restrictions[s][
                        "succeedingShiftTypes"
                    ]:
                        if (
                            shifts[n][d + 1][
                                utils.shift_to_int[forbidden_shift_succession]
                            ]
                            == 1
                        ):
                            print(
                                f"{n} {d} {s} {shifts[n][d][s]} {shifts[n][d + 1][utils.shift_to_int[forbidden_shift_succession]]}"
                            )
                            return False
            last_shift = utils.shift_to_int[
                self.constants["h0_data_original"]["nurseHistory"][n][
                    "lastAssignedShiftType"
                ]
            ]
            if last_shift == utils.shift_to_int["None"]:
                break
            if restrictions[last_shift]["succeedingShiftTypes"] == []:
                break
            for forbidden_shift_succession in restrictions[last_shift][
                "succeedingShiftTypes"
            ]:
                if shifts[n][0][utils.shift_to_int[forbidden_shift_succession]] == 1:
                    print(
                        f"{n} {s} {last_shift} {utils.shift_to_int[forbidden_shift_succession]}"
                    )
                    return False

        return True

    def is_min_max_consecutive_assignments_satisfied(self):
        if not self.is_max_consecutive_work_days_satisfied():
            return False
        if not self.is_min_consecutive_work_days_satisfied():
            return False
        if not self.is_max_consecutive_work_shifts_satisfied():
            return False
        if not self.is_min_consecutive_work_shifts_satisfied():
            return False
        return True

    def is_min_max_consecutive_days_off_satisfied(self):
        if not self.is_max_consecutive_days_off_satisfied():
            return False
        if not self.is_min_consecutive_days_off_satisfied():
            return False
        return True

    def is_min_max_total_assignments_satisfied(self):
        if not self.is_max_total_assignments_satisfied():
            return False
        if not self.is_min_total_assignments_satisfied():
            return False
        return True

    def is_max_total_assignments_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            max_total_assignments = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfAssignmentsHard"]

            if (
                sum(
                    [
                        self.help_vars["shifts"][n][d][s]
                        for d in self.all_days
                        for s in all_shifts
                    ]
                )
                > max_total_assignments
            ):
                print(f"n_{n}_max{max_total_assignments}")
                return False

        return True

    def is_max_total_incomplete_weekends_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        all_weeks = self.constants["all_weeks"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            max_total_incomplete_weekends = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfIncompleteWeekendsHard"]

            total_incomplete_weekends = 0
            for w in all_weeks:
                if sum(self.help_vars["working_days"][n][w * 7 + 5: w * 7 + 7]) == 1:
                    total_incomplete_weekends += 1

            if total_incomplete_weekends > max_total_incomplete_weekends:
                print(
                    f"n_{n}_max{max_total_incomplete_weekends}_actual{total_incomplete_weekends}"
                )
                return False

        return True

    def is_min_free_period_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        all_weeks = self.constants["all_weeks"]
        all_days = self.constants["all_days"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            min_free_period = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimalFreePeriod"]

            for w in all_weeks:
                counter = 0
                max_found_period = 0
                for d in all_days:
                    if self.help_vars["working_days"][n][w * 7 + d] == 0:
                        counter += 1
                        if counter >= max_found_period:
                            max_found_period = counter
                    else:
                        counter = 0
                if max_found_period < min_free_period:
                    print(f"n_{n}")
                    return False

        return True

    def is_min_total_assignments_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            if self.is_nurse_on_vacation_any_week(n):
                continue

            min_total_assignments = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfAssignmentsHard"]

            if (
                sum(
                    [
                        self.help_vars["shifts"][n][d][s]
                        for d in self.all_days
                        for s in all_shifts
                    ]
                )
                < min_total_assignments
            ):
                print(f"n_{n}_min{min_total_assignments}")
                return False

        return True

    def is_max_consecutive_work_days_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            counter = self.constants["h0_data_original"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveWorkingDaysHard"]

            for d in self.all_days:
                if self.help_vars["working_days"][n][d] == 0:
                    counter = 0
                counter += self.help_vars["working_days"][n][d]
                if counter > max_consecutive_working_days:
                    print(f"n_{n}_{d}_max{max_consecutive_working_days}")
                    return False
        return True

    def is_max_consecutive_days_off_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            counter = self.constants["h0_data_original"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            max_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveDaysOffHard"]

            for d in self.all_days:
                w = math.floor(d / 7)
                if self.constants["configuration"]["h12"] and (
                    self.help_vars["nurses_ids_on_vacation"][w]
                ):
                    counter = 0
                    continue
                if self.help_vars["working_days"][n][d] == 1:
                    counter = 0
                counter += 1 - self.help_vars["working_days"][n][d]
                if counter > max_consecutive_days_off:
                    print(f"n_{n}_{d}_max{max_consecutive_days_off}")
                    return False
        return True

    def is_min_consecutive_work_days_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            prev = self.constants["h0_data_original"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            counter = prev
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDaysHard"]

            for d in self.all_days:
                w = math.floor(d / 7)
                if self.constants["configuration"]["h12"] and (
                    self.help_vars["nurses_ids_on_vacation"][w]
                ):
                    counter = 0
                    continue
                if self.help_vars["working_days"][n][d] == 0:
                    if counter > 0 and counter < min_consecutive_working_days:
                        print(f"n_{n}_{d}_min{min_consecutive_working_days}_prev{prev}")
                        return False
                    counter = 0
                counter += self.help_vars["working_days"][n][d]
        return True

    def is_min_consecutive_days_off_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            prev = self.constants["h0_data_original"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            counter = prev
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOffHard"]

            for d in self.all_days:
                if self.help_vars["working_days"][n][d] == 1:
                    if counter > 0 and counter < min_consecutive_days_off:
                        print(f"n_{n}_{d}_min{min_consecutive_days_off}_prev{prev}")
                        return False
                    counter = 0
                counter += 1 - self.help_vars["working_days"][n][d]
        return True

    def is_max_consecutive_work_shifts_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                self.constants["h0_data_original"]["nurseHistory"][n][
                    "lastAssignedShiftType"
                ]
            ]
            consecutive_shifts_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveAssignments"]
            for s in all_shifts:
                max_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "maximumNumberOfConsecutiveAssignmentsHard"
                ]
                counter = 0
                if last_shift == s:
                    counter = consecutive_shifts_prev_week
                for d in self.all_days:
                    if self.help_vars["shifts"][n][d][s] == 0:
                        counter = 0
                    counter += self.help_vars["shifts"][n][d][s]
                    if counter > max_consecutive_working_shifts:
                        print(f"n_{n}_d_{d}_s_{s}_max{max_consecutive_working_shifts}")
                        return False

        return True

    def is_min_consecutive_work_shifts_satisfied(self):
        all_nurses = self.constants["all_nurses"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                self.constants["h0_data_original"]["nurseHistory"][n][
                    "lastAssignedShiftType"
                ]
            ]
            consecutive_shifts_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveAssignments"]
            for s in reversed(all_shifts):
                min_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "minimumNumberOfConsecutiveAssignmentsHard"
                ]
                counter = 0
                if last_shift == s:
                    counter = consecutive_shifts_prev_week
                for d in self.all_days:
                    w = math.floor(d / 7)
                    if self.constants["configuration"]["h12"] and (
                        n in self.help_vars["nurses_ids_on_vacation"][w]
                    ):
                        counter = 0
                        continue

                    if self.help_vars["shifts"][n][d][s] == 0:
                        if counter > 0 and counter < min_consecutive_working_shifts:
                            if (
                                self.help_vars["shifts"][n][d - 1][0] == 1
                                and self.help_vars["shifts"][n][d - 1][3] == 1
                            ):
                                counter = 0
                                continue
                            print(
                                f"n_{n}_d_{d}_s_{s}_min{min_consecutive_working_shifts}_prevshift{consecutive_shifts_prev_week}"
                            )
                            return False
                        counter = 0
                    counter += self.help_vars["shifts"][n][d][s]

        return True

    def compute_helpful_values(self):
        num_nurses = self.constants["num_nurses"]
        num_skills = self.constants["num_skills"]
        num_shifts = self.constants["num_shifts"]
        all_weeks = self.constants["all_weeks"]
        working_days = [[0 for _ in self.all_days] for _ in range(num_nurses)]
        shifts = [
            [[0 for _ in range(num_shifts)] for _ in self.all_days]
            for _ in range(num_nurses)
        ]
        shifts_and_skills = [
            [
                [[0 for _ in range(num_skills)] for _ in range(num_shifts)]
                for _ in self.all_days
            ]
            for _ in range(num_nurses)
        ]

        for n in range(num_nurses):
            for d in self.all_days:
                for s in range(num_shifts):
                    for sk in range(num_skills):
                        self.schedule[(n, d, s, sk)] = round(
                            self.schedule[(n, d, s, sk)]
                        )
                        shifts_and_skills[n][d][s][sk] = self.schedule[(n, d, s, sk)]
                    shifts[n][d][s] = sum(
                        [self.schedule[(n, d, s, sk)] for sk in range(num_skills)]
                    )
                working_days[n][d] = utils.isPositiveNumber(sum(shifts[n][d][:]))

        nurses_ids_on_vacation = [
            list(
                map(
                    lambda x: int(x.split("_")[1]),
                    self.constants["all_wd_data"][w]["vacations"],
                )
            )
            for w in all_weeks
        ]

        ret_val = {}
        ret_val["working_days"] = working_days
        ret_val["shifts"] = shifts
        ret_val["shifts_and_skills"] = shifts_and_skills
        ret_val["nurses_ids_on_vacation"] = nurses_ids_on_vacation

        return ret_val

    @utils.soft_constr_value_print
    def get_optimal_capacity_value(self) -> int:
        subtotal = 0
        all_weeks = self.constants["all_weeks"]

        for w in all_weeks:
            requirements = self.constants["all_wd_data"][w]["requirements"]

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
                        self.help_vars["shifts_and_skills"][n][d + 7 * w][s][sk]
                        for n in all_nurses
                    ]
                    diff = opt_capacity > sum(skills_worked)
                    if diff > 0:
                        subtotal += diff
        return subtotal * utils.OPT_CAPACITY_WEIGHT

    @utils.soft_constr_value_print
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
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_working_days_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveWorkingDays"]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveWorkingDays"]
            for d in self.all_days:
                if d > max_consecutive_working_days:
                    diff = (
                        sum(
                            self.help_vars["working_days"][n][
                                d - max_consecutive_working_days: d + 1
                            ]
                        )
                        - max_consecutive_working_days
                    )
                    if diff > 0:
                        subtotal += diff
                else:
                    if (
                        consecutive_working_days_prev_week
                        >= max_consecutive_working_days - d
                    ):
                        diff = sum(self.help_vars["working_days"][n][0: d + 1]) - d
                        if diff > 0:
                            subtotal += diff

        return subtotal * utils.CONS_WORK_DAY_WEIGHT

    def get_max_consecutive_shifts_value(self) -> int:
        all_nurses = self.constants["all_nurses"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        subtotal = 0

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                self.constants["h0_data_original"]["nurseHistory"][n][
                    "lastAssignedShiftType"
                ]
            ]
            consecutive_shifts_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveAssignments"]
            for s in all_shifts:
                max_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "maximumNumberOfConsecutiveAssignments"
                ]
                for d in self.all_days:
                    if d >= max_consecutive_working_shifts:
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
        sc_data = self.constants["sc_data"]

        subtotal = 0

        for n in all_nurses:
            consecutive_working_days_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveWorkingDays"]
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in self.all_days:
                w = math.floor(d / 7)
                if self.constants["configuration"]["h12"] and (
                    n in self.help_vars["nurses_ids_on_vacation"][w]
                ):
                    continue
                for dd in range(1, min_consecutive_working_days):
                    if (d - dd) > 0:
                        diff = (
                            (1 - self.help_vars["working_days"][n][d])
                            + sum(self.help_vars["working_days"][n][d - dd:d])
                            + (1 - self.help_vars["working_days"][n][d - dd - 1])
                            - (dd + 1)
                        )
                        if diff > 0:
                            subtotal += diff * utils.CONS_WORK_DAY_WEIGHT * dd

                    else:
                        if consecutive_working_days_prev_week == dd - d:
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
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_working_shifts_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveAssignments"]
            lastAssignedShiftType = self.constants["h0_data_original"]["nurseHistory"][
                n
            ]["lastAssignedShiftType"]
            lastShittTypeAsInt = utils.shift_to_int[lastAssignedShiftType]
            for d in self.all_days:
                w = math.floor(d / 7)
                if self.constants["configuration"]["h12"] and (
                    n in self.help_vars["nurses_ids_on_vacation"][w]
                ):
                    continue
                for s in all_shifts:
                    if self.help_vars["shifts"][n][d][s] == 1:
                        continue
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
                                # print(f'diff{diff}_d{d}_dd{dd}_shifts{self.help_vars["shifts"]}')
                                subtotal += utils.CONS_SHIFT_WEIGHT
                        else:
                            # print(f's{s}_d{d}_dd{dd}_shifts{self.help_vars["shifts"]}_prev{consecutive_working_shifts_prev_week}_min{min_consecutive_shifts}')
                            if (consecutive_working_shifts_prev_week == dd - d) and (
                                lastShittTypeAsInt == s
                            ):
                                working_shifts = sum(
                                    [
                                        self.help_vars["shifts"][n][ddd][s]
                                        for ddd in range(d + 1)
                                    ]
                                )
                                if working_shifts < d + 1:
                                    print(f'diff{working_shifts}_d{d}_dd{dd}_shifts{self.help_vars["shifts"]}_prev{consecutive_working_shifts_prev_week}')
                                    subtotal += utils.CONS_SHIFT_WEIGHT
                            # if lastShittTypeAsInt != s:

        return subtotal

    @utils.soft_constr_value_print
    def get_consecutive_days_off_value(self) -> int:
        subtotal = 0
        subtotal += self.get_max_consecutive_days_off_value()
        subtotal += self.get_min_consecutive_days_off_value()
        return subtotal

    def get_max_consecutive_days_off_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_days_off_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveDaysOff"]
            max_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveDaysOff"]
            for d in self.all_days:
                if d > max_consecutive_days_off:
                    if (
                        sum(
                            self.help_vars["working_days"][n][
                                d - max_consecutive_days_off:d + 1
                            ]
                        )
                        == 0
                    ):
                        subtotal += 1
                else:
                    if consecutive_days_off_prev_week >= max_consecutive_days_off - d:
                        if sum(self.help_vars["working_days"][n][0:d + 1]) == 0:
                            subtotal += 1
        return subtotal * utils.CONS_DAY_OFF_WEIGHT

    def get_min_consecutive_days_off_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            consecutive_days_off_prev_week = self.constants["h0_data_original"][
                "nurseHistory"
            ][n]["numberOfConsecutiveDaysOff"]
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in self.all_days:
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
                            subtotal += 1
                    else:
                        if consecutive_days_off_prev_week >= min_consecutive_days_off:
                            continue
                        if consecutive_days_off_prev_week == 0:
                            continue
                        if consecutive_days_off_prev_week == dd - d:
                            working_days = (
                                sum(
                                    [
                                        self.help_vars["working_days"][n][ddd]
                                        for ddd in range(0, d + 1)
                                    ]
                                )
                            
                            )
                            if working_days > 0:
                                subtotal += 1
        return subtotal * utils.CONS_DAY_OFF_WEIGHT

    @utils.soft_constr_value_print
    def get_assignment_preferences_value(self) -> int:
        subtotal = 0
        for w in self.constants["all_weeks"]:
            for preference in self.constants["all_wd_data"][w]["shiftOffRequests"]:
                nurse_id = int(preference["nurse"].split("_")[1])
                day_id = utils.day_to_int[preference["day"]]
                shift_id = utils.shift_to_int[preference["shiftType"]]

                if shift_id != utils.shift_to_int["Any"]:
                    if self.help_vars["shifts"][nurse_id][day_id][shift_id] == 1:
                        subtotal += 1
                else:
                    if self.help_vars["working_days"][nurse_id][day_id] == 1:
                        subtotal += 1
        return subtotal * utils.UNSATISFIED_PREFERENCE_WEIGHT

    @utils.soft_constr_value_print
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
                    subtotal += 1
        return subtotal * utils.INCOMPLETE_WEEKEDN_WEIGHT

    @utils.soft_constr_value_print
    def get_total_assignments_out_of_limits_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            max_total_assignments = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfAssignments"]
            min_total_assignments = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfAssignments"]

            total_assignments = sum(
                [
                    self.help_vars["shifts"][n][d][s]
                    for d in self.all_days
                    for s in all_shifts
                ]
            )
            if total_assignments > max_total_assignments:
                subtotal += total_assignments - max_total_assignments
            if total_assignments < min_total_assignments:
                if not self.is_nurse_on_vacation_any_week(n):
                    subtotal += min_total_assignments - total_assignments
        return subtotal * utils.TOTAL_ASSIGNMENTS_WEIGHT

    def get_total_uses_of_ifneeded_skills_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            ifneeded_skills = sc_data["nurses"][n]["skillsIfNeeded"]
            total_assignments_to_ifneeded_skill = sum(
                [
                    self.help_vars["shifts"][n][d][utils.skill_to_int[s]]
                    for d in self.all_days
                    for s in ifneeded_skills
                ]
            )
            subtotal += total_assignments_to_ifneeded_skill
        return subtotal * utils.TOTAL_IFNEEDED_SKILL_WEIGHT

    def get_unsatisfied_overtime_preferences_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        all_shifts = self.constants["all_shifts"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            min_total_assignments = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfAssignmentsHard"]
            wanted_overtime = sc_data["nurses"][n]["wantedOvertime"]
            ideal_total_assignments = min_total_assignments + wanted_overtime

            total_assignments = sum(
                [
                    self.help_vars["shifts"][n][d][s]
                    for d in self.all_days
                    for s in all_shifts
                ]
            )
            if total_assignments < ideal_total_assignments:
                if not self.is_nurse_on_vacation_any_week(n):
                    subtotal += ideal_total_assignments - total_assignments
        return subtotal * utils.UNSATISFIED_OVERTIME_PREFERENCE_WEIGHT

    @utils.soft_constr_value_print
    def get_total_weekends_over_limit_value(self) -> int:
        subtotal = 0
        all_nurses = self.constants["all_nurses"]
        all_weeks = self.constants["all_weeks"]
        sc_data = self.constants["sc_data"]

        for n in all_nurses:
            max_total_weekends = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfWorkingWeekends"]

            total_working_weekends = 0
            for w in all_weeks:
                if sum(self.help_vars["working_days"][n][w*7 + 5: (w+1)*7]) > 0:
                    total_working_weekends += 1

            if total_working_weekends > max_total_weekends:
                subtotal += total_working_weekends - max_total_weekends
        return subtotal * utils.TOTAL_WORKING_WEEKENDS_WEIGHT

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
        all_shifts = self.constants["all_shifts"]
        all_skills = self.constants["all_skills"]

        for n in all_nurses:
            upper_limit = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["maximumNumberOfAssignments"]

            lower_limit = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["minimumNumberOfAssignments"]

            total_assignments = sum(
                [
                    self.schedule[(n, d, s, sk)]
                    for d in self.all_days
                    for s in all_shifts
                    for sk in all_skills
                ]
            )
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
                if (
                    sum(
                        [
                            self.schedule[(n, 5 + 7 * w, s, sk)]
                            + self.schedule[(n, 6 + 7 * w, s, sk)]
                            for s in all_shifts
                            for sk in all_skills
                        ]
                    )
                    > 0
                ):
                    total_working_weekends += 1
            diff = total_working_weekends - worked_weekends_limit
            if diff > 0:
                subtotal += diff * utils.TOTAL_WORKING_WEEKENDS_WEIGHT
        return subtotal

    def print_current_week(self):
        num_days = self.constants["num_days"]
        num_nurses = self.constants["num_nurses"]
        num_skills = self.constants["num_skills"]
        num_shifts = self.constants["num_shifts"]
        for n in range(num_nurses):
            for d in range(num_days):
                for s in range(num_shifts):
                    for sk in range(num_skills):
                        print(
                            f'{self.help_vars["shifts_and_skills"][n][d][s][sk]} ',
                            end="",
                        )
                    print("|", end="")
                print("||", end="")
            print()

        for n in range(num_nurses):
            for d in range(num_days):
                for s in range(num_shifts):
                    print(
                        f'{self.help_vars["shifts"][n][d][s]} ',
                        end="",
                    )
                print("|", end="")
            print()

    def is_nurse_on_vacation_any_week(self, nurse_id):
        return self.constants["configuration"]["h12"] and (
            nurse_id
            in [
                id
                for w in self.constants["all_weeks"]
                for id in self.help_vars["nurses_ids_on_vacation"][w]
            ]
        )
