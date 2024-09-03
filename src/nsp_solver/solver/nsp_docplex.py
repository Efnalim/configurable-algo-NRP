#!/usr/bin/python

import math

from nsp_solver.solver.nsp_solver import NSP_solver

from docplex.cp.model import CpoModel

from nsp_solver.utils import utils

max_consecutive_work_days = 7
max_consecutive_days_off = 7


class DOCPLEX_Solver(NSP_solver):
    """Child Class from NSP_solver that uses CP solver from docplex API to compute a schedule per week.
    """
    name = 'DOCPLEX'

    def init_cp_vars(self, model, data):
        """
        Initializes basic variables for primarly for hard contraints.
        Returns a dictionary 'basic_cp_vars' containing the names of those variables for further manipulation.
        """

        all_skills = data["all_skills"]
        all_shifts = data["all_shifts"]
        all_days = data["all_days"]
        all_nurses = data["all_nurses"]
        wd_data = data["wd_data"]

        minimal_capacities = [
            [[0 for _ in all_skills] for _ in all_shifts] for _ in all_days
        ]

        for req in wd_data["requirements"]:
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
                minimal_capacities[d][s][sk] = min_capacity
                # print(f"req_shift_with_skill_min_{min_capacity}")

        # Creates shifts variables.
        # shifts[n][d][s]: nurse 'n' works shift 's' on day 'd' if 1 does not work if 0.

        shifts_with_skills = [
            [
                [
                    [
                        model.integer_var(
                            min=0,
                            max=1,
                            name=f"shifts_with_skills_n{n}_d{d}_s{s}sk{sk}",
                        )
                        for sk in all_skills
                    ]
                    for s in all_shifts
                ]
                for d in all_days
            ]
            for n in all_nurses
        ]

        shifts = [
            [
                [
                    model.integer_var(
                        min=0,
                        max=1,
                        name=f"shift_n{n}_d{d}_s{s}",
                    )
                    for s in all_shifts
                ]
                for d in all_days
            ]
            for n in all_nurses
        ]

        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.add(
                        sum([shifts_with_skills[n][d][s][sk] for sk in all_skills])
                        == shifts[n][d][s]
                    )

        working_days = [
            [
                model.integer_var(
                    min=0,
                    max=1,
                    name=f"work_day_n{n}_d{d}",
                )
                for d in all_days
            ]
            for n in all_nurses
        ]

        for n in all_nurses:
            for d in all_days:
                model.add(sum([shifts[n][d][s] for s in all_shifts]) == working_days[n][d])

        basic_cp_vars = {}
        basic_cp_vars["shifts_with_skills"] = shifts_with_skills
        basic_cp_vars["working_days"] = working_days
        basic_cp_vars["shifts"] = shifts
        basic_cp_vars["minimal_capacities"] = minimal_capacities
        return basic_cp_vars

    def add_shift_succession_reqs(
        self, model, shifts, all_nurses, all_days, all_shifts, num_days, data, basic_cp_vars
    ):
        """
        Adds hard constraint that disables invalid pairs of succcessive shift types.
        """

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                data["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]
            if last_shift == 2:
                model.add(
                    sum([shifts[n][0][0], shifts[n][0][1]]) == 0
                )
            if last_shift == 3:
                model.add(
                    sum(
                        [
                            shifts[n][0][0],
                            shifts[n][0][1],
                            shifts[n][0][2],
                        ]
                    )
                    == 0
                )

            for d in range(num_days - 1):
                for s in all_shifts:
                    if s == 2:
                        model.add(
                            sum(
                                [
                                    shifts[n][d][s],
                                    shifts[n][d + 1][s - 1],
                                    shifts[n][d + 1][s - 2],
                                ]
                            )
                            <= 1
                        )
                    if s == 3:
                        model.add(
                            sum(
                                [
                                    shifts[n][d][s],
                                    shifts[n][d + 1][s - 1],
                                    shifts[n][d + 1][s - 2],
                                    shifts[n][d + 1][s - 3],
                                ]
                            )
                            <= 1
                        )

    def add_missing_skill_req(
        self,
        model,
        nurses_data,
        shifts_with_skills,
        all_days,
        all_shifts,
        all_skills,
    ):
        """
        Adds hard constraint that disables nurses working shift with a skill that they do not possess.
        """

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
                            model.add(shifts_with_skills[n][d][s][sk] == 0)

    def add_hard_constrains(self, model, basic_cp_vars, data):
        """
        Adds all hard constraints to the model.
        """

        all_nurses = data["all_nurses"]
        all_shifts = data["all_shifts"]
        all_days = data["all_days"]
        all_skills = data["all_skills"]
        num_days = data["num_days"]
        sc_data = data["sc_data"]
        wd_data = data["wd_data"]
        shifts = basic_cp_vars["shifts"]
        shifts_with_skills = basic_cp_vars["shifts_with_skills"]

        # Each nurse works at most one shift per day and minimal number of nurses for each shift and each skill must be satisfied
        for n in all_nurses:
            for d in all_days:
                model.add(
                    sum(
                        [
                            shifts_with_skills[n][d][s][sk]
                            for sk in all_skills
                            for s in all_shifts
                        ]
                    )
                    <= 1
                )

        self.add_shift_succession_reqs(
            model,
            shifts,
            all_nurses,
            all_days,
            all_shifts,
            num_days,
            data,
            basic_cp_vars,
        )
        self.add_missing_skill_req(
            model,
            sc_data["nurses"],
            shifts_with_skills,
            all_days,
            all_shifts,
            all_skills,
        )
        for req in wd_data["requirements"]:
            self.add_shift_skill_req_minimal(model, req, basic_cp_vars, data)

    def add_shift_skill_req_minimal(self, model, req, basic_cp_vars, data):
        """
        Adds hard constraint that dictates minimal number of nurses in a shift working with specific skill.
        """

        all_nurses = data["all_nurses"]
        shifts_with_skills = basic_cp_vars["shifts_with_skills"]

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
            model.add(
                sum([shifts_with_skills[n][d][s][sk] for n in all_nurses])
                >= min_capacity
            )

    def init_cp_vars_for_soft_constraints(self, model, basic_cp_vars, data):
        """Adds variables used by the soft constraints.

        Args:
            model: object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

        Returns:
            dict: the variables added to the mathematical model
        """
        all_nurses = data["all_nurses"]
        all_shifts = data["all_shifts"]
        all_skills = data["all_skills"]
        all_days = data["all_days"]
        num_days = data["num_days"]
        shifts = basic_cp_vars["shifts"]
        working_days = basic_cp_vars["working_days"]
        sc_data = data["sc_data"]

        # Creates insufficient staffing variables.
        # shifts[(d,s,sk)]: number of nurses under optimal number for day d shift s and skill sk
        insufficient_staffing = {}
        for d in all_days:
            for s in all_shifts:
                for sk in all_skills:
                    insufficient_staffing[(d, s, sk)] = model.integer_var(
                        min=0, max=10, name=f"insufficient_staffing_d{d}_s{s}_sk{sk}"
                    )

        # Creates unsatisfied preferences variables.
        # unsatisfied_preferences_n{n}_d{d}_s{s} of nurse n for day d and shift s
        unsatisfied_preferences = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    unsatisfied_preferences[(n, d, s)] = model.integer_var(
                        min=0, max=1, name=f"unsatisfied_preferences_n{n}_d{d}_s{s}"
                    )

        # Vars for each nurse how many days they worked
        total_working_days = {}
        for n in all_nurses:
            total_working_days[(n)] = model.integer_var(
                min=0, max=num_days + 1, name=f"total_working_days_n{n}"
            )

        for n in all_nurses:
            model.add(total_working_days[(n)] == sum(working_days[n][:]))

        # Vars for each nurse n indicationg if they were working on weekend this week
        working_weekends = {}
        for n in all_nurses:
            working_weekends[(n)] = model.integer_var(
                min=0, max=1, name=f"working_weekends_n{n}"
            )

        # Vars for each nurse n indicationg if how many weekends were they working up to this week over the limit
        total_working_weekends_over_limit = {}
        for n in all_nurses:
            total_working_weekends_over_limit[(n)] = model.integer_var(
                min=0, max=4, name=f"total_working_weekends_over_limit_n{n}"
            )

        incomplete_weekends = {}
        for n in all_nurses:
            incomplete_weekends[(n)] = model.integer_var(
                min=0, max=1, name=f"incomplete_weekends_n{n}"
            )

        total_working_days_over_limit = {}
        total_working_days_under_limit = {}
        for n in all_nurses:
            total_working_days_over_limit[(n)] = model.integer_var(
                min=0, max=7, name=f"total_working_days_over_limit_n{n}"
            )
            total_working_days_under_limit[(n)] = model.integer_var(
                min=0, max=7, name=f"total_working_days_under_limit_n{n}"
            )

        violations_of_max_consecutive_working_days = {}
        for n in all_nurses:
            for d in all_days:
                violations_of_max_consecutive_working_days[(n, d)] = model.integer_var(
                    min=0,
                    max=1,
                    name=f"violations_of_max_consecutive_working_days_n{n}_d{d}",
                )

        violations_of_max_consecutive_working_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    violations_of_max_consecutive_working_shifts[(n, d, s)] = (
                        model.integer_var(
                            min=0,
                            max=1,
                            name=f"violations_of_max_consecutive_working_shifts_n{n}_d{d}_s{s}",
                        )
                    )

        violations_of_max_consecutive_days_off = {}
        for n in all_nurses:
            for d in all_days:
                violations_of_max_consecutive_days_off[(n, d)] = model.integer_var(
                    min=0, max=1, name=f"violations_of_max_consecutive_days_off_n{n}_d{d}"
                )

        violations_of_min_consecutive_days_off = {}
        for n in all_nurses:
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    violations_of_min_consecutive_days_off[(n, d, dd)] = model.integer_var(
                        min=0,
                        max=1,
                        name=f"violations_of_min_consecutive_days_off_n{n}_d{d}_dd{dd}",
                    )

        violations_of_min_consecutive_working_days = {}
        for n in all_nurses:
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    violations_of_min_consecutive_working_days[(n, d, dd)] = (
                        model.integer_var(
                            min=0,
                            max=1,
                            name=f"violations_of_min_consecutive_working_days_n{n}_d{d}_dd{dd}",
                        )
                    )

        violations_of_min_consecutive_working_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_working_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignments"
                    ]
                    for dd in range(1, min_consecutive_working_shifts):
                        violations_of_min_consecutive_working_shifts[(n, d, s, dd)] = (
                            model.integer_var(
                                min=0,
                                max=1,
                                name=f"violations_of_min_consecutive_working_shifts_n{n}_d{d}_s{s}_dd{dd}",
                            )
                        )

        not_working_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    not_working_shifts[(n, d, s)] = model.integer_var(
                        min=0, max=1, name=f"not_workingshift_n{n}_d{d}_s{s}"
                    )

        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.add(sum([not_working_shifts[(n, d, s)], shifts[n][d][s]]) == 1)

        not_working_days = {}
        for n in all_nurses:
            for d in all_days:
                not_working_days[(n, d)] = model.integer_var(
                    min=0, max=1, name=f"not_working_day_n{n}_d{d}"
                )

        for n in all_nurses:
            for d in all_days:
                model.add(sum([not_working_days[(n, d)], working_days[n][d]]) == 1)

        soft_cp_vars = {}
        soft_cp_vars["insufficient_staffing"] = insufficient_staffing
        soft_cp_vars["unsatisfied_preferences"] = unsatisfied_preferences
        soft_cp_vars["total_working_days"] = total_working_days
        soft_cp_vars["working_weekends"] = working_weekends
        soft_cp_vars["total_working_weekends_over_limit"] = (
            total_working_weekends_over_limit
        )
        soft_cp_vars["total_working_days_over_limit"] = total_working_days_over_limit
        soft_cp_vars["total_working_days_under_limit"] = total_working_days_under_limit
        soft_cp_vars["incomplete_weekends"] = incomplete_weekends
        soft_cp_vars["violations_of_max_consecutive_working_days"] = (
            violations_of_max_consecutive_working_days
        )
        soft_cp_vars["violations_of_max_consecutive_days_off"] = (
            violations_of_max_consecutive_days_off
        )
        soft_cp_vars["violations_of_max_consecutive_working_shifts"] = (
            violations_of_max_consecutive_working_shifts
        )
        soft_cp_vars["not_working_days"] = not_working_days
        soft_cp_vars["not_working_shifts"] = not_working_shifts
        soft_cp_vars["violations_of_min_consecutive_working_days"] = (
            violations_of_min_consecutive_working_days
        )
        soft_cp_vars["violations_of_min_consecutive_days_off"] = (
            violations_of_min_consecutive_days_off
        )
        soft_cp_vars["violations_of_min_consecutive_working_shifts"] = (
            violations_of_min_consecutive_working_shifts
        )

        return soft_cp_vars

    def add_shift_skill_req_optimal(self, model, req, basic_cp_vars, soft_cp_vars, data):
        """Add

        Args:
            model : object that represents the mathematical model
            req (dict): requirements for the coverage
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        all_nurses = data["all_nurses"]
        shifts_with_skills = basic_cp_vars["shifts_with_skills"]
        insufficient_staffing = soft_cp_vars["insufficient_staffing"]

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
            model.add(
                sum(
                    [insufficient_staffing[(d, s, sk)]]
                    + [shifts_with_skills[n][d][s][sk] for n in all_nurses]
                )
                >= opt_capacity
            )

    def add_insatisfied_preferences_reqs(
        self, model, wd_data, basic_cp_vars, soft_cp_vars, data
    ):
        """Adds the soft constraint that introduces the preferences of nurses for specific assignments/non-assignments.

        Args:
            model : object that represents the mathematical model
            wd_data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        unsatisfied_preferences = soft_cp_vars["unsatisfied_preferences"]
        shifts = basic_cp_vars["shifts"]

        for preference in wd_data["shiftOffRequests"]:
            nurse_id = int(preference["nurse"].split("_")[1])
            day_id = utils.day_to_int[preference["day"]]
            shift_id = utils.shift_to_int[preference["shiftType"]]

            if shift_id != utils.shift_to_int["Any"]:
                model.add(
                    (
                        unsatisfied_preferences[(nurse_id, day_id, shift_id)]
                        - shifts[nurse_id][day_id][shift_id]
                    )
                    == 0
                )

    def add_total_working_weekends_soft_constraints(
        self, model, basic_cp_vars, soft_cp_vars, data, week_number
    ):
        """Adds the soft constraint that penilizes more working weekends than the specified maximum.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week
        """
        sc_data = data["sc_data"]
        h0_data = data["h0_data"]
        total_working_weekends_over_limit = soft_cp_vars[
            "total_working_weekends_over_limit"
        ]
        working_weekends = soft_cp_vars["working_weekends"]

        all_nurses = data["all_nurses"]
        num_weeks = data["num_weeks"]
        working_days = basic_cp_vars["working_days"]

        for n in all_nurses:
            model.add(working_weekends[(n)] - working_days[n][5] == 0)
            model.add(working_weekends[(n)] - working_days[n][6] == 0)

        for n in all_nurses:
            worked_weekends_limit_for_this_week = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfWorkingWeekends"] * ((week_number + 1) / num_weeks)
            worked_weekends_in_previous_weeks = h0_data["nurseHistory"][n][
                "numberOfWorkingWeekends"
            ]
            model.add(
                (-total_working_weekends_over_limit[(n)] + working_weekends[(n)])
                <= worked_weekends_limit_for_this_week - worked_weekends_in_previous_weeks
            )

    def add_incomplete_weekends_constraint(self, model, basic_cp_vars, soft_cp_vars, data):
        """Adds the soft constraint that penilizes incomplete weekends.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        nurses_data = data["sc_data"]["nurses"]
        contracts_data = data["sc_data"]["contracts"]
        incomplete_weekends = soft_cp_vars["incomplete_weekends"]
        working_weekends = soft_cp_vars["working_weekends"]
        working_days = basic_cp_vars["working_days"]
        all_nurses = data["all_nurses"]

        for n in all_nurses:
            isCompleteWeekendRequested = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["completeWeekends"]
            if isCompleteWeekendRequested == 1:
                model.add(
                    2 * working_weekends[(n)]
                    - incomplete_weekends[(n)]
                    - working_days[n][5]
                    - working_days[n][6]
                    == 0
                )

    def add_total_working_days_out_of_bounds_constraint(
        self, model, basic_cp_vars, soft_cp_vars, data, week_number
    ):
        """Adds the soft constraint that penilizes total assignments out of bounds specified in the contract of each nurse.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week
        """
        nurses_data = data["sc_data"]["nurses"]
        contracts_data = data["sc_data"]["contracts"]
        total_working_days = soft_cp_vars["total_working_days"]
        total_working_days_over_limit = soft_cp_vars["total_working_days_over_limit"]
        total_working_days_under_limit = soft_cp_vars["total_working_days_under_limit"]
        all_nurses = data["all_nurses"]
        num_weeks = data["num_weeks"]
        h0_data = data["h0_data"]

        for n in all_nurses:
            worked_days_in_previous_weeks = h0_data["nurseHistory"][n][
                "numberOfAssignments"
            ]
            upper_limit = math.ceil(
                contracts_data[utils.contract_to_int[nurses_data[n]["contract"]]][
                    "maximumNumberOfAssignments"
                ]
                * ((week_number + 1) / num_weeks)
            )
            lower_limit = math.ceil(
                contracts_data[utils.contract_to_int[nurses_data[n]["contract"]]][
                    "minimumNumberOfAssignments"
                ]
                * ((week_number + 1) / num_weeks)
            )
            model.add(
                (-total_working_days_over_limit[(n)] + total_working_days[(n)])
                < upper_limit - worked_days_in_previous_weeks
            )
            model.add(
                (total_working_days_under_limit[(n)] + total_working_days[(n)])
                > lower_limit - worked_days_in_previous_weeks
            )

    def add_max_consecutive_work_days_constraint(
        self, model, basic_cp_vars, soft_cp_vars, data
    ):
        """Adds the soft constraint that penilizes assignment of a number of consecutive working days over the maximum specified in the constract of each nurse.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_max_consecutive_working_days = soft_cp_vars[
            "violations_of_max_consecutive_working_days"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        sc_data = data["sc_data"]
        working_days = basic_cp_vars["working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.add(
                        sum(
                            [-violations_of_max_consecutive_working_days[(n, d)]]
                            + working_days[n][d - max_consecutive_working_days: d + 1]
                        )
                        <= max_consecutive_working_days
                    )
                else:
                    if (
                        consecutive_working_days_prev_week
                        >= max_consecutive_working_days - d
                    ):
                        model.add(
                            sum(
                                [-violations_of_max_consecutive_working_days[(n, d)]]
                                + working_days[n][0: d + 1]
                            )
                            <= d
                        )

        for n in all_nurses:
            consecutive_working_days_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            max_consecutive_working_days = max_consecutive_work_days
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.add(
                        sum(
                            working_days[n][d - max_consecutive_working_days: d + 1],
                            [1] * (max_consecutive_working_days + 1),
                        )
                        <= max_consecutive_working_days
                    )
                else:
                    if (
                        consecutive_working_days_prev_week
                        >= max_consecutive_working_days - d
                    ):
                        model.add(sum(working_days[n][0: d + 1]) <= d)

    def add_min_consecutive_work_days_constraint(
        self, model, basic_cp_vars, soft_cp_vars, data
    ):
        """
        Adds the soft constraint that penilizes assignment of a number of consecutive working days under the minimum specified in the constract of each nurse.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_min_consecutive_working_days = soft_cp_vars[
            "violations_of_min_consecutive_working_days"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        sc_data = data["sc_data"]
        working_days = basic_cp_vars["working_days"]
        not_working_days = soft_cp_vars["not_working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    if (d - dd) > 0:
                        model.add(
                            sum(
                                [-violations_of_min_consecutive_working_days[(n, d, dd)]]
                                + [not_working_days[(n, d)]]
                                + working_days[n][d - dd: d]
                                + [not_working_days[(n, d - dd - 1)]]
                            )
                            <= dd + 1
                        )
                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            model.add(
                                sum(
                                    [violations_of_min_consecutive_working_days[(n, d, dd)]]
                                    + [not_working_days[(n, d)]]
                                    + working_days[n][0:d]
                                )
                                <= d
                            )

    def add_min_consecutive_shifts_constraint(
        self, model, basic_cp_vars, soft_cp_vars, data
    ):
        """Adds the soft constraint that penilizes assignment of a number of consecutive shifts of one type under the minimum specified in the scenario.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_min_consecutive_working_shifts = soft_cp_vars[
            "violations_of_min_consecutive_working_shifts"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        all_shifts = data["all_shifts"]
        sc_data = data["sc_data"]
        shifts = basic_cp_vars["shifts"]
        not_working_shifts = soft_cp_vars["not_working_shifts"]

        for n in all_nurses:
            consecutive_working_shifts_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            lastAssignedShiftType = data["h0_data"]["nurseHistory"][n][
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
                            model.add(
                                sum(
                                    [
                                        -violations_of_min_consecutive_working_shifts[
                                            (n, d, s, dd)
                                        ]
                                    ]
                                    + [not_working_shifts[(n, d, s)]]
                                    + list((shifts[n][ddd][s]) for ddd in range(d - dd, d))
                                    + [not_working_shifts[(n, d - dd - 1, s)]]
                                )
                                <= dd + 1
                            )
                        else:
                            if (consecutive_working_shifts_prev_week == d - dd) and (
                                lastShittTypeAsInt == s
                            ):
                                model.add(
                                    sum(
                                        [
                                            -violations_of_min_consecutive_working_shifts[
                                                (n, d, s, dd)
                                            ]
                                        ]
                                        + [not_working_shifts[(n, d, s)]]
                                        + list((shifts[n][ddd][s]) for ddd in range(d))
                                    )
                                    <= d
                                )

    def add_min_consecutive_days_off_constraint(
        self, model, basic_cp_vars, soft_cp_vars, data
    ):
        """Adds the soft constraint that penilizes a number of consecutive days off under the minimum specified in the contract of each nurse.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_min_consecutive_days_off = soft_cp_vars[
            "violations_of_min_consecutive_days_off"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        sc_data = data["sc_data"]
        working_days = basic_cp_vars["working_days"]
        not_working_days = soft_cp_vars["not_working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    if (d - dd) > 0:
                        model.add(
                            sum(
                                [-violations_of_min_consecutive_days_off[(n, d, dd)]]
                                + [working_days[n][d]]
                                + list(
                                    not_working_days[(n, ddd)] for ddd in range(d - dd, d)
                                )
                                + [working_days[n][d - dd - 1]]
                            )
                            <= dd + 1
                        )
                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            model.add(
                                sum(
                                    [-violations_of_min_consecutive_days_off[(n, d, dd)]]
                                    + [working_days[n][d]]
                                    + list(
                                        not_working_days[(n, ddd)] for ddd in range(0, d)
                                    )
                                )
                                <= d
                            )

    def add_max_consecutive_work_shifts_constraint(
        self, model, basic_cp_vars, soft_cp_vars, data
    ):
        """Adds the soft constraint that penilizes assignment of any number of consecutive shifts of one type over the maximum specified in the scenario.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_max_consecutive_working_shifts = soft_cp_vars[
            "violations_of_max_consecutive_working_shifts"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        all_shifts = data["all_shifts"]
        sc_data = data["sc_data"]
        shifts = basic_cp_vars["shifts"]

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                data["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]
            consecutive_shifts_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveAssignments"
            ]
            for s in all_shifts:
                max_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "maximumNumberOfConsecutiveAssignments"
                ]
                for d in all_days:
                    if d > max_consecutive_working_shifts:
                        model.add(
                            sum(
                                [-violations_of_max_consecutive_working_shifts[(n, d, s)]]
                                + list(
                                    shifts[n][d - dd][s]
                                    for dd in range(1 + max_consecutive_working_shifts)
                                )
                            )
                            <= max_consecutive_working_shifts
                        )
                    else:
                        if (last_shift == s) and (
                            consecutive_shifts_prev_week
                            >= max_consecutive_working_shifts - d
                        ):
                            model.add(
                                sum(
                                    [
                                        -violations_of_max_consecutive_working_shifts[
                                            (n, d, s)
                                        ]
                                    ]
                                    + list(shifts[n][dd][s] for dd in range(d + 1))
                                )
                                <= d
                            )

    def add_max_consecutive_days_off_constraint(
        self, model, basic_cp_vars, soft_cp_vars, data
    ):
        """Adds the soft constraint that bans assignment of any number of consecutive days off over the maximum specified in the contract of each nurse.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_max_consecutive_days_off = soft_cp_vars[
            "violations_of_max_consecutive_days_off"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        sc_data = data["sc_data"]
        working_days = basic_cp_vars["working_days"]

        for n in all_nurses:
            consecutive_days_off_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.add(
                        sum(
                            [violations_of_max_consecutive_days_off[(n, d)]]
                            + working_days[n][d - max_consecutive_working_days: d + 1]
                        )
                        >= 1
                    )
                else:
                    if consecutive_days_off_prev_week >= max_consecutive_working_days - d:
                        model.add(
                            sum(
                                [violations_of_max_consecutive_days_off[(n, d)]]
                                + working_days[n][0: d + 1]
                            )
                            >= 1
                        )

        for n in all_nurses:
            consecutive_days_off_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            max_consecutive_working_days = max_consecutive_days_off
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.add(
                        sum(working_days[n][d - max_consecutive_working_days: d + 1]) >= 1
                    )
                else:
                    if consecutive_days_off_prev_week >= max_consecutive_working_days - d:
                        model.add(sum(working_days[n][0: d + 1]) >= 1)

    def add_soft_constraints(self, model, basic_cp_vars, soft_cp_vars, data, week_number):
        """Adds the soft constraints to the model.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week
        """
        wd_data = data["wd_data"]

        for req in wd_data["requirements"]:
            self.add_shift_skill_req_optimal(model, req, basic_cp_vars, soft_cp_vars, data)

        self.add_insatisfied_preferences_reqs(
            model, wd_data, basic_cp_vars, soft_cp_vars, data
        )

        self.add_total_working_weekends_soft_constraints(
            model, basic_cp_vars, soft_cp_vars, data, week_number
        )

        self.add_total_working_days_out_of_bounds_constraint(
            model, basic_cp_vars, soft_cp_vars, data, week_number
        )

        self.add_incomplete_weekends_constraint(model, basic_cp_vars, soft_cp_vars, data)

        self.add_max_consecutive_work_days_constraint(
            model, basic_cp_vars, soft_cp_vars, data
        )

        self.add_max_consecutive_work_shifts_constraint(
            model, basic_cp_vars, soft_cp_vars, data
        )

        self.add_max_consecutive_days_off_constraint(
            model, basic_cp_vars, soft_cp_vars, data
        )

        self.add_min_consecutive_work_days_constraint(
            model, basic_cp_vars, soft_cp_vars, data
        )

        self.add_min_consecutive_days_off_constraint(
            model, basic_cp_vars, soft_cp_vars, data
        )

        self.add_min_consecutive_shifts_constraint(model, basic_cp_vars, soft_cp_vars, data)

        # self.add_total_working_days_out_of_bounds_constraint_hard(model, basic_cp_vars, soft_cp_vars, data, week_number)

        return

    def save_tmp_results(
        self, results, sol, data, basic_cp_vars, soft_cp_vars, week_number, model
    ):
        """Stores the solution into the results dictionary.

        Args:
            results (dict): dictionary used to store partially computed schedule
            sol : object that contains the computed solution
            data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            week_number (int): number of the computed week
            model : object that represents the mathematical model
        """
        num_days = data["num_days"]
        num_nurses = data["num_nurses"]
        num_skills = data["num_skills"]
        num_shifts = data["num_shifts"]
        shifts_with_skills = basic_cp_vars["shifts_with_skills"]

        if sol:
            results[(week_number, "status")] = sol.get_solve_status()
            results[(week_number, "value")] = sol.get_objective_value()
            results[(week_number, "allweeksoft")] = 0
            results[("allweeksoft")] = 0
            results[(week_number, "status")] = utils.STATUS_OK

            for n in range(num_nurses):
                for d in range(num_days):
                    for s in range(num_shifts):
                        for sk in range(num_skills):
                            results[(n, d + 7 * week_number, s, sk)] = 0
                            results[(n, d + 7 * week_number, s, sk)] = sol[
                                shifts_with_skills[n][d][s][sk]
                            ]
        else:
            print("No solution found")

    def set_objective_function(self, model, data, basic_cp_vars, soft_cp_vars):
        """Sets the objective function contatining all penalties from all enabled constraints.

        Args:
            model : object that represents the mathematical model
            data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
        """
        all_nurses = data["all_nurses"]
        all_shifts = data["all_shifts"]
        all_skills = data["all_skills"]
        all_days = data["all_days"]
        sc_data = data["sc_data"]

        insufficient_staffing = soft_cp_vars["insufficient_staffing"]
        unsatisfied_preferences = soft_cp_vars["unsatisfied_preferences"]
        total_working_weekends_over_limit = soft_cp_vars[
            "total_working_weekends_over_limit"
        ]
        incomplete_weekends = soft_cp_vars["incomplete_weekends"]
        total_working_days_over_limit = soft_cp_vars["total_working_days_over_limit"]
        total_working_days_under_limit = soft_cp_vars["total_working_days_under_limit"]
        violations_of_max_consecutive_working_days = soft_cp_vars[
            "violations_of_max_consecutive_working_days"
        ]
        violations_of_max_consecutive_working_shifts = soft_cp_vars[
            "violations_of_max_consecutive_working_shifts"
        ]
        violations_of_max_consecutive_days_off = soft_cp_vars[
            "violations_of_max_consecutive_days_off"
        ]
        violations_of_min_consecutive_working_days = soft_cp_vars[
            "violations_of_min_consecutive_working_days"
        ]
        violations_of_min_consecutive_days_off = soft_cp_vars[
            "violations_of_min_consecutive_days_off"
        ]
        violations_of_min_consecutive_working_shifts = soft_cp_vars[
            "violations_of_min_consecutive_working_shifts"
        ]

        summed_violations_of_min_cons_working_days = []
        weights_of_violations_of_min_cons_working_days = []
        for n in all_nurses:
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    summed_violations_of_min_cons_working_days.append(
                        violations_of_min_consecutive_working_days[(n, d, dd)]
                    )
                    weights_of_violations_of_min_cons_working_days.append(30 * dd)

        summed_violations_of_min_cons_days_off = []
        weights_of_violations_of_min_cons_days_off = []
        for n in all_nurses:
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    summed_violations_of_min_cons_days_off.append(
                        violations_of_min_consecutive_days_off[(n, d, dd)]
                    )
                    weights_of_violations_of_min_cons_days_off.append(30 * dd)

        summed_violations_of_min_cons_shift_type = []
        weights_of_violations_of_min_cons_shift_type = []
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignments"
                    ]
                    for dd in range(1, min_consecutive_shifts):
                        summed_violations_of_min_cons_shift_type.append(
                            violations_of_min_consecutive_working_shifts[(n, d, s, dd)]
                        )
                        weights_of_violations_of_min_cons_shift_type.append(15 * dd)

        model.add(
            model.minimize(
                (
                    sum(
                        insufficient_staffing[(d, s, sk)]
                        for d in all_days
                        for s in all_shifts
                        for sk in all_skills
                    )
                    * 30
                )
                + (
                    sum(
                        unsatisfied_preferences[(n, d, s)]
                        for n in all_nurses
                        for d in all_days
                        for s in all_shifts
                    )
                    * 10
                )
                + (sum(total_working_weekends_over_limit[(n)] for n in all_nurses) * 30)
                + (sum(incomplete_weekends[(n)] for n in all_nurses) * 30)
                + (sum(total_working_days_over_limit[(n)] for n in all_nurses) * 20)
                + (sum(total_working_days_under_limit[(n)] for n in all_nurses) * 20)
                + (
                    sum(
                        violations_of_max_consecutive_working_days[(n, d)]
                        for n in all_nurses
                        for d in all_days
                    )
                    * 30
                )
                + (
                    sum(
                        violations_of_max_consecutive_days_off[(n, d)]
                        for n in all_nurses
                        for d in all_days
                    )
                    * 30
                )
                + (
                    sum(
                        violations_of_max_consecutive_working_shifts[(n, d, s)]
                        for n in all_nurses
                        for d in all_days
                        for s in all_shifts
                    )
                    * 15
                )
                + (
                    sum(
                        [
                            x * y
                            for x, y in zip(
                                summed_violations_of_min_cons_working_days,
                                weights_of_violations_of_min_cons_working_days,
                            )
                        ]
                    )
                )
                + (
                    sum(
                        [
                            x * y
                            for x, y in zip(
                                summed_violations_of_min_cons_working_days,
                                weights_of_violations_of_min_cons_working_days,
                            )
                        ]
                    )
                )
                + (
                    sum(
                        [
                            x * y
                            for x, y in zip(
                                summed_violations_of_min_cons_days_off,
                                weights_of_violations_of_min_cons_days_off,
                            )
                        ]
                    )
                )
                + (
                    sum(
                        [
                            x * y
                            for x, y in zip(
                                summed_violations_of_min_cons_shift_type,
                                weights_of_violations_of_min_cons_shift_type,
                            )
                        ]
                    )
                )
            )
        )

    def setup_problem(self, c, data, week_number):
        """Sets up the mathematical model to be solved.

        Args:
            model: object that represents the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week

        Returns:
            (dict, dict): 2 dictionaries that contains names of variables of the mathematical model
        """
        # Create ILP variables.
        basic_cp_vars = self.init_cp_vars(c, data)

        # Add hard constrains to model
        self.add_hard_constrains(c, basic_cp_vars, data)

        soft_cp_vars = {}
        soft_cp_vars = self.init_cp_vars_for_soft_constraints(c, basic_cp_vars, data)

        self.add_soft_constraints(c, basic_cp_vars, soft_cp_vars, data, week_number)

        self.set_objective_function(c, data, basic_cp_vars, soft_cp_vars)

        return basic_cp_vars, soft_cp_vars

    def compute_one_week(self, time_limit_for_week, data, results):
        """Computes a schedule for a week given a time limit and data.

        Args:
            time_limit_for_week (int): time limit for finding a schedule as optimal as possible
            data (dict): dictionary that contains data from input files
            results (dict): dictionary used to store partially computed schedule
        """
        week_number = data["h0_data"]["week"]
        mdl = CpoModel()

        # c.parameters.mip.display.set(0)
        # c.parameters.output.clonelog.set(0)
        # c.parameters.simplex.display.set(0)
        # c.parameters.timelimit.set(time_limit_for_week)
        # c.parameters.mip.tolerances.absmipgap.set(0.0)
        # c.parameters.emphasis.mip.set(
        #     c.parameters.emphasis.mip.values.optimality)

        basic_cp_vars, soft_cp_vars = self.setup_problem(mdl, data, week_number)

        # msol = mdl.solve(TimeLimit=10)
        msol = mdl.solve(TimeLimit=time_limit_for_week, Workers=1, LogVerbosity='Quiet')
        if msol:
            self.save_tmp_results(
                results, msol, data, basic_cp_vars, soft_cp_vars, week_number, mdl
            )
        else:
            results[(week_number, "status")] = utils.STATUS_FAIL
            print("No solution")
            # sol = c.solution
