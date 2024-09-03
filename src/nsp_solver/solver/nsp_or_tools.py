#!/usr/bin/python

from nsp_solver.solver.nsp_solver import NSP_solver
from nsp_solver.utils import utils
from ortools.sat.python import cp_model

import math

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


class ORTOOLS_Solver(NSP_solver):
    """Child Class from NSP_solver that uses CP SAT solver from OR-TOOLS to compute a schedule per week.
    """
    name = 'ORTOOLS'

    def init_cp_vars(self, model, data):
        """
        Initializes basic variables for primarly for hard contraints.
        Returns a dictionary 'basic_cp_vars' containing the names of those variables for further manipulation.
        """
        all_nurses = data["all_nurses"]
        all_shifts = data["all_shifts"]
        all_days = data["all_days"]
        all_skills = data["all_skills"]

        # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
        shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    shifts[(n, d, s)] = model.NewBoolVar(f"shift_n{n}_d{d}_s{s}")

        working_days = {}
        for n in all_nurses:
            for d in all_days:
                working_days[(n, d)] = model.NewBoolVar(f"shift_n{n}_d{d}")

        # Creates shifts_with_skills variables.
        # shifts_with_skills[(n, d, s, sk)]: nurse 'n' works shift 's' on day 'd' with skill 'sk'.
        shifts_with_skills = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    for sk in all_skills:
                        shifts_with_skills[(n, d, s, sk)] = model.NewBoolVar(
                            f"shift_n{n}_d{d}_s{s}_sk{sk}"
                        )

        insufficient_staffing = {}
        for d in all_days:
            for s in all_shifts:
                for sk in all_skills:
                    insufficient_staffing[(d, s, sk)] = model.NewIntVar(
                        0, 10, f"insufficient_staffing_d{d}_s{s}_sk{sk}"
                    )

        basic_CP_vars = {}
        basic_CP_vars["working_days"] = working_days
        basic_CP_vars["shifts"] = shifts
        basic_CP_vars["shifts_with_skills"] = shifts_with_skills
        basic_CP_vars["insufficient_staffing"] = insufficient_staffing
        return basic_CP_vars

    def init_cp_vars_for_soft_constraints(self, model, basic_CP_vars, data):
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
        all_days = data["all_days"]
        num_days = data["num_days"]
        shifts = basic_CP_vars["shifts"]
        working_days = basic_CP_vars["working_days"]
        sc_data = data["sc_data"]
        history_data = data["h0_data"]

        # Preferences for shifts off
        unsatisfied_preferences = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    unsatisfied_preferences[(n, d, s)] = model.NewBoolVar(
                        f"unsatisfied_preferences_n{n}_d{d}_s{s}"
                    )

        # Vars for each nurse how many days they worked
        total_working_days = {}
        for n in all_nurses:
            total_working_days[(n)] = model.NewIntVar(
                0, num_days, f"total_working_days_n{n}"
            )

        for n in all_nurses:
            days_worked = []
            for d in all_days:
                for s in all_shifts:
                    days_worked.append(shifts[(n, d, s)])
            model.Add(sum(days_worked) == total_working_days[(n)])

        # Vars for each nurse n indicationg if they were working on weekend w
        working_weekends = {}
        for n in all_nurses:
            working_weekends[(n)] = model.NewBoolVar(f"working_weekends_n{n}")
            model.Add(working_days[(n, 5)] + working_days[(n, 6)] >= working_weekends[(n)])
            model.Add(working_days[(n, 5)] <= working_weekends[(n)])
            model.Add(working_days[(n, 6)] <= working_weekends[(n)])
            # model.Add(sum(shifts_worked_on_saturday) + sum(shifts_worked_on_sunday) >= working_weekends[(n, w)])

        total_working_weekends_over_limit = {}
        for n in all_nurses:
            total_working_weekends_over_limit[(n)] = model.NewIntVar(
                0, 4, f"total_working_weekends_over_limit_n{n}"
            )

        total_incomplete_weekends = {}
        for n in all_nurses:
            total_incomplete_weekends[(n)] = model.NewIntVar(
                0, 4, f"total_incomplete_weekends_n{n}"
            )

        total_working_days_over_limit = {}
        total_working_days_under_limit = {}
        for n in all_nurses:
            total_working_days_over_limit[(n)] = model.NewIntVar(
                0, num_days, f"total_working_days_over_limit_n{n}"
            )
            total_working_days_under_limit[(n)] = model.NewIntVar(
                0, num_days, f"total_working_days_under_limit_n{n}"
            )

        violations_of_max_consecutive_working_days = {}
        violations_of_max_consecutive_working_days_for_nurse = {}
        for n in all_nurses:
            violations_of_max_consecutive_working_days_for_nurse[(n)] = model.NewIntVar(
                0, num_days, f"violations_of_max_consecutive_working_days_for_nurse{n}"
            )
            all_violation_for_nurse = []
            max_consecutive_working_days = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                if d + max_consecutive_working_days >= num_days:
                    break
                violations_of_max_consecutive_working_days[
                    (n, d + max_consecutive_working_days)
                ] = model.NewBoolVar(
                    f"violations_of_max_consecutive_working_days_n{n}_d{d + max_consecutive_working_days}"
                )
                all_violation_for_nurse.append(
                    violations_of_max_consecutive_working_days[
                        (n, d + max_consecutive_working_days)
                    ]
                )
                working_days_to_sum = []
                for dd in range(max_consecutive_working_days + 1):
                    for s in all_shifts:
                        working_days_to_sum.append(shifts[(n, d + dd, s)])
                model.Add(
                    violations_of_max_consecutive_working_days[
                        (n, d + max_consecutive_working_days)
                    ]
                    >= (sum(working_days_to_sum) - max_consecutive_working_days)
                )

            violations_of_max_consecutive_working_days_from_prev_week = {}
            prev_week_consecutive_working_days = history_data["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            if prev_week_consecutive_working_days > 0:
                for d in range(max_consecutive_working_days):
                    if prev_week_consecutive_working_days - d == 0:
                        break

                    violations_of_max_consecutive_working_days_from_prev_week[(n, d)] = (
                        model.NewBoolVar(
                            f"violations_of_max_consecutive_working_days_from_prev_week{n}_d{d}"
                        )
                    )
                    all_violation_for_nurse.append(
                        violations_of_max_consecutive_working_days_from_prev_week[(n, d)]
                    )

                    working_days_to_sum = []
                    for dd in range(max_consecutive_working_days - d):
                        working_days_to_sum.append(working_days[(n, d)])
                    model.Add(
                        violations_of_max_consecutive_working_days_from_prev_week[(n, d)]
                        >= (sum(working_days_to_sum) + d + 1 - max_consecutive_working_days)
                    )

            model.Add(
                violations_of_max_consecutive_working_days_for_nurse[(n)]
                == sum(all_violation_for_nurse)
            )

        violations_of_max_consecutive_working_shifts = {}
        violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type = {}
        for n in all_nurses:
            for s in all_shifts:
                violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type[
                    (n, s)
                ] = model.NewIntVar(
                    0,
                    num_days,
                    f"violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type_n{n}_s{s}",
                )
                all_violation_for_nurse_for_shift_type = []
                max_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "maximumNumberOfConsecutiveAssignments"
                ]
                for d in all_days:
                    if d + max_consecutive_working_shifts >= num_days:
                        break
                    violations_of_max_consecutive_working_shifts[
                        (n, s, d + max_consecutive_working_shifts)
                    ] = model.NewBoolVar(
                        f"violations_of_max_consecutive_working_shifts_n{n}_s{s}_d{d + max_consecutive_working_shifts}"
                    )
                    all_violation_for_nurse_for_shift_type.append(
                        violations_of_max_consecutive_working_shifts[
                            (n, s, d + max_consecutive_working_shifts)
                        ]
                    )
                    working_shifts_to_sum = []
                    for dd in range(max_consecutive_working_shifts + 1):
                        working_shifts_to_sum.append(shifts[(n, d + dd, s)])
                    model.Add(
                        violations_of_max_consecutive_working_shifts[
                            (n, s, d + max_consecutive_working_shifts)
                        ]
                        >= (sum(working_shifts_to_sum) - max_consecutive_working_shifts)
                    )
                model.Add(
                    violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type[
                        (n, s)
                    ]
                    == sum(all_violation_for_nurse_for_shift_type)
                )

        violations_of_max_consecutive_days_off = {}
        violations_of_max_consecutive_days_off_for_nurse = {}
        for n in all_nurses:
            violations_of_max_consecutive_days_off_for_nurse[(n)] = model.NewIntVar(
                0, num_days, f"violations_of_max_consecutive_days_off_for_nurse{n}"
            )
            all_violation_for_nurse = []
            max_consecutive_days_off = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                if d + max_consecutive_days_off >= num_days:
                    break
                violations_of_max_consecutive_days_off[
                    (n, d + max_consecutive_days_off)
                ] = model.NewBoolVar(
                    f"violations_of_max_consecutive_days_off_n{n}_d{d + max_consecutive_working_days}"
                )
                all_violation_for_nurse.append(
                    violations_of_max_consecutive_days_off[
                        (n, d + max_consecutive_days_off)
                    ]
                )
                days_off_to_sum = []
                for dd in range(max_consecutive_days_off + 1):
                    for s in all_shifts:
                        days_off_to_sum.append(shifts[(n, d + dd, s)])
                model.Add(
                    violations_of_max_consecutive_days_off[
                        (n, d + max_consecutive_days_off)
                    ]
                    >= 1 - (sum(days_off_to_sum))
                )
            model.Add(
                violations_of_max_consecutive_days_off_for_nurse[(n)]
                == sum(all_violation_for_nurse)
            )

        violations_of_min_consecutive_days_off = {}
        for n in all_nurses:
            min_consecutive_days_off = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    violations_of_min_consecutive_days_off[(n, d, dd)] = model.NewBoolVar(
                        f"violations_of_min_consecutive_days_off_n{n}_d{d}_dd{dd}"
                    )

        violations_of_min_consecutive_working_days = {}
        for n in all_nurses:
            min_consecutive_working_days = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    violations_of_min_consecutive_working_days[(n, d, dd)] = (
                        model.NewBoolVar(
                            f"violations_of_min_consecutive_working_days_n{n}_d{d}_dd{dd}"
                        )
                    )

        violations_of_min_consecutive_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_working_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignments"
                    ]
                    for dd in range(1, min_consecutive_working_shifts):
                        violations_of_min_consecutive_shifts[(n, d, s, dd)] = (
                            model.NewBoolVar(
                                f"violations_of_min_consecutive_shifts_n{n}_d{d}_s{s}_dd{dd}"
                            )
                        )

        not_working_days = {}
        for n in all_nurses:
            for d in all_days:
                not_working_days[(n, d)] = model.NewBoolVar(f"not_working_day_n{n}_d{d}")
                model.Add(not_working_days[(n, d)] + working_days[(n, d)] == 1)

        not_working_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    not_working_shifts[(n, d, s)] = model.NewBoolVar(
                        f"not_working_shift_n{n}_d{d}"
                    )
                    model.Add(not_working_shifts[(n, d, s)] + shifts[(n, d, s)] == 1)

        soft_CP_vars = {}
        soft_CP_vars["unsatisfied_preferences"] = unsatisfied_preferences
        soft_CP_vars["total_working_days"] = total_working_days
        soft_CP_vars["working_weekends"] = working_weekends
        soft_CP_vars["not_working_days"] = not_working_days
        soft_CP_vars["not_working_shifts"] = not_working_shifts
        soft_CP_vars["total_working_weekends_over_limit"] = (
            total_working_weekends_over_limit
        )
        soft_CP_vars["total_working_days_over_limit"] = total_working_days_over_limit
        soft_CP_vars["total_working_days_under_limit"] = total_working_days_under_limit
        soft_CP_vars["total_incomplete_weekends"] = total_incomplete_weekends
        soft_CP_vars["violations_of_max_consecutive_working_days_for_nurse"] = (
            violations_of_max_consecutive_working_days_for_nurse
        )
        soft_CP_vars["violations_of_max_consecutive_days_off_for_nurse"] = (
            violations_of_max_consecutive_days_off_for_nurse
        )
        soft_CP_vars[
            "violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type"
        ] = violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type
        soft_CP_vars["violations_of_min_consecutive_days_off"] = (
            violations_of_min_consecutive_days_off
        )
        soft_CP_vars["violations_of_min_consecutive_working_days"] = (
            violations_of_min_consecutive_working_days
        )
        soft_CP_vars["violations_of_min_consecutive_shifts"] = (
            violations_of_min_consecutive_shifts
        )

        return soft_CP_vars

    def add_hard_constrains(self, model, basic_CP_vars, data):
        """
        Adds all hard constraints to the model.
        """
        all_nurses = data["all_nurses"]
        all_shifts = data["all_shifts"]
        all_days = data["all_days"]
        all_skills = data["all_skills"]
        num_days = data["num_days"]
        sc_data = data["sc_data"]
        shifts = basic_CP_vars["shifts"]
        working_days = basic_CP_vars["working_days"]
        shifts_with_skills = basic_CP_vars["shifts_with_skills"]
        # Each nurse works at most one shift per day.
        for n in all_nurses:
            for d in all_days:
                model.AddAtMostOne(shifts[(n, d, s)] for s in all_shifts)

        # Each nurse works at most one skill per day.
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.AddAtMostOne(
                        shifts_with_skills[(n, d, s, sk)] for sk in all_skills
                    )

        # If nurse is working with skill that shift, she is working that shift.
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    skills_worked = []
                    for sk in all_skills:
                        skills_worked.append(shifts_with_skills[(n, d, s, sk)])
                    model.Add(sum(skills_worked) == shifts[(n, d, s)])

        for n in all_nurses:
            for d in all_days:
                shifts_worked = []
                for s in all_shifts:
                    shifts_worked.append(shifts[(n, d, s)])
                model.Add(sum(shifts_worked) == working_days[(n, d)])

        self.add_shift_succession_reqs(
            model, shifts, all_nurses, all_days, all_shifts, num_days, data
        )
        self.add_missing_skill_req(
            model, sc_data["nurses"], shifts_with_skills, all_days, all_shifts, all_skills
        )
        return

    def add_soft_constraints(self, model, basic_CP_vars, soft_CP_vars, data):
        """Adds the soft constraints to the model.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week
        """
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        all_shifts = data["all_shifts"]
        all_skills = data["all_skills"]
        sc_data = data["sc_data"]
        h0_data = data["h0_data"]
        wd_data = data["wd_data"]
        shifts = basic_CP_vars["shifts"]
        working_days = basic_CP_vars["working_days"]
        unsatisfied_preferences = soft_CP_vars["unsatisfied_preferences"]
        total_working_days = soft_CP_vars["total_working_days"]
        total_working_days_over_limit = soft_CP_vars["total_working_days_over_limit"]
        total_incomplete_weekends = soft_CP_vars["total_incomplete_weekends"]
        working_weekends = soft_CP_vars["working_weekends"]
        total_working_weekends_over_limit = soft_CP_vars[
            "total_working_weekends_over_limit"
        ]
        total_working_days_under_limit = soft_CP_vars["total_working_days_under_limit"]
        total_incomplete_weekends = soft_CP_vars["total_incomplete_weekends"]

        self.add_insatisfied_preferences_reqs(
            model,
            wd_data["shiftOffRequests"],
            unsatisfied_preferences,
            shifts,
            all_nurses,
            all_days,
            all_shifts,
            all_skills,
        )

        self.add_total_working_days_out_of_bounds_constraint(
            model,
            sc_data["nurses"],
            sc_data["contracts"],
            h0_data["nurseHistory"],
            total_working_days,
            total_working_days_over_limit,
            total_working_days_under_limit,
            all_nurses,
        )

        self.add_total_incomplete_weekends_constraint(
            model,
            sc_data["nurses"],
            sc_data["contracts"],
            total_incomplete_weekends,
            working_weekends,
            shifts,
            working_days,
            all_nurses,
            all_days,
            all_shifts,
        )

        self.add_total_working_weekends_soft_constraints(
            model,
            sc_data["nurses"],
            sc_data["contracts"],
            h0_data["nurseHistory"],
            total_working_weekends_over_limit,
            working_weekends,
            all_nurses,
        )

        self.add_min_consecutive_days_off_constraint(
            model, basic_CP_vars, soft_CP_vars, data
        )

        self.add_min_consecutive_working_days_constraint(
            model, basic_CP_vars, soft_CP_vars, data
        )

        self.add_min_consecutive_shifts_constraint(
            model, basic_CP_vars, soft_CP_vars, data
        )

        return

    def add_min_consecutive_days_off_constraint(
        self, model, basic_CP_vars, soft_CP_vars, data
    ):
        """Adds the soft constraint that penilizes a number of consecutive days off under the minimum specified in the contract of each nurse.

        Args:
            model: object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_min_consecutive_days_off = soft_CP_vars[
            "violations_of_min_consecutive_days_off"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        sc_data = data["sc_data"]
        working_days = basic_CP_vars["working_days"]
        not_working_days = soft_CP_vars["not_working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            min_consecutive_days_off = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    if (d - dd) > 0:
                        model.Add(
                            dd + 1
                            >= sum(
                                [-violations_of_min_consecutive_days_off[(n, d, dd)]]
                                + [working_days[(n, d)]]
                                + list(
                                    not_working_days[(n, ddd)] for ddd in range(d - dd, d)
                                )
                                + [working_days[(n, d - dd - 1)]]
                            )
                        )
                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            model.Add(
                                dd + 1
                                >= sum(
                                    [-violations_of_min_consecutive_days_off[(n, d, dd)]]
                                    + [working_days[(n, d)]]
                                    + list(
                                        not_working_days[(n, ddd)] for ddd in range(0, d)
                                    )
                                )
                            )

    def add_min_consecutive_working_days_constraint(
        self, model, basic_CP_vars, soft_CP_vars, data
    ):
        """
        Adds the soft constraint that penilizes assignment of a number of consecutive working days under the minimum specified in the constract of each nurse.

        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_min_consecutive_working_days = soft_CP_vars[
            "violations_of_min_consecutive_working_days"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        sc_data = data["sc_data"]
        working_days = basic_CP_vars["working_days"]
        not_working_days = soft_CP_vars["not_working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            min_consecutive_working_days = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    if (d - dd) > 0:
                        model.Add(
                            dd + 1
                            >= sum(
                                [-violations_of_min_consecutive_working_days[(n, d, dd)]]
                                + [not_working_days[(n, d)]]
                                + list(working_days[(n, ddd)] for ddd in range(d - dd, d))
                                + [not_working_days[(n, d - dd - 1)]]
                            )
                        )
                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            model.Add(
                                dd + 1
                                >= sum(
                                    [
                                        -violations_of_min_consecutive_working_days[
                                            (n, d, dd)
                                        ]
                                    ]
                                    + [not_working_days[(n, d)]]
                                    + list(working_days[(n, ddd)] for ddd in range(0, d))
                                )
                            )

    def add_min_consecutive_shifts_constraint(
        self, model, basic_CP_vars, soft_CP_vars, data
    ):
        """Adds the soft constraint that penilizes assignment of a number of consecutive shifts of one type under the minimum specified in the scenario.

        Args:
            model: object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        """
        violations_of_min_consecutive_shifts = soft_CP_vars[
            "violations_of_min_consecutive_shifts"
        ]
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        all_shifts = data["all_shifts"]
        sc_data = data["sc_data"]
        working_days = basic_CP_vars["working_days"]
        not_working_shifts = soft_CP_vars["not_working_shifts"]

        for n in all_nurses:
            consecutive_working_shifts_prev_week = data["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            lastAssignedShiftType = data["h0_data"]["nurseHistory"][n][
                "lastAssignedShiftType"
            ]
            lastShittTypeAsInt = shift_to_int[lastAssignedShiftType]
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignments"
                    ]
                    for dd in range(1, min_consecutive_shifts):
                        if (d - dd) > 0:
                            model.Add(
                                dd + 1
                                >= sum(
                                    [-violations_of_min_consecutive_shifts[(n, d, s, dd)]]
                                    + [not_working_shifts[(n, d, s)]]
                                    + list(
                                        working_days[(n, ddd)] for ddd in range(d - dd, d)
                                    )
                                    + [not_working_shifts[(n, d - dd - 1, s)]]
                                )
                            )
                        else:
                            if (consecutive_working_shifts_prev_week == d - dd) and (
                                lastShittTypeAsInt == s
                            ):
                                model.Add(
                                    dd + 1
                                    >= sum(
                                        [
                                            -violations_of_min_consecutive_shifts[
                                                (n, d, s, dd)
                                            ]
                                        ]
                                        + [not_working_shifts[(n, d, s)]]
                                        + list(
                                            working_days[(n, ddd)] for ddd in range(0, d)
                                        )
                                    )
                                )

    def add_total_incomplete_weekends_constraint(
        self,
        model,
        nurses_data,
        contracts_data,
        total_incomplete_weekends,
        working_weekends,
        shifts,
        working_days,
        all_nurses,
        all_days,
        all_shifts,
    ):
        """Adds the soft constraint that penilizes incomplete weekends.
        """
        incomplete_weekends = {}
        for n in all_nurses:
            isCompleteWeekendRequested = contracts_data[
                contract_to_int[nurses_data[n]["contract"]]
            ]["completeWeekends"]
            if isCompleteWeekendRequested == 1:
                incomplete_weekends[(n)] = model.NewBoolVar(f"incomplete_weekends_n{n}")
                model.Add(
                    incomplete_weekends[(n)]
                    == 2 * working_weekends[(n)]
                    - working_days[(n, 5)]
                    - working_days[(n, 6)]
                )

        for n in all_nurses:
            isCompleteWeekendRequested = contracts_data[
                contract_to_int[nurses_data[n]["contract"]]
            ]["completeWeekends"]
            if isCompleteWeekendRequested == 1:
                incomplete_weekends_n = []
                incomplete_weekends_n.append(incomplete_weekends[(n)])
                model.Add(total_incomplete_weekends[(n)] == sum(incomplete_weekends_n))
        return

    def add_total_working_days_out_of_bounds_constraint(
        self,
        model,
        nurses_data,
        contracts_data,
        history,
        total_working_days,
        total_working_days_over_limit,
        total_working_days_under_limit,
        all_nurses,
    ):
        """Adds the soft constraint that penilizes more working weekends than the specified maximum.
        """
        for n in all_nurses:
            upper_limit = (
                math.ceil(
                    contracts_data[contract_to_int[nurses_data[n]["contract"]]][
                        "maximumNumberOfAssignments"
                    ]
                    / 4
                )
                + 1
            )
            lower_limit = (
                math.ceil(
                    contracts_data[contract_to_int[nurses_data[n]["contract"]]][
                        "minimumNumberOfAssignments"
                    ]
                    / 4
                )
                - 1
            )
            model.Add(
                total_working_days_over_limit[(n)] >= total_working_days[(n)] - upper_limit
            )
            model.Add(
                total_working_days_under_limit[(n)] >= lower_limit - total_working_days[(n)]
            )
        return

    def add_shift_skill_req(self, model, req, basic_CP_vars, soft_CP_vars, data):
        """Adds hard constraint that dictates minimal number of nurses in a shift working with specific skill.
        """
        all_nurses = data["all_nurses"]
        shifts_with_skills = basic_CP_vars["shifts_with_skills"]
        insufficient_staffing = basic_CP_vars["insufficient_staffing"]

        shift = shift_to_int[req["shiftType"]]
        skill = skill_to_int[req["skill"]]
        minimal_capacities_in_week = [
            req["requirementOnMonday"]["minimum"],
            req["requirementOnTuesday"]["minimum"],
            req["requirementOnWednesday"]["minimum"],
            req["requirementOnThursday"]["minimum"],
            req["requirementOnFriday"]["minimum"],
            req["requirementOnSaturday"]["minimum"],
            req["requirementOnSunday"]["minimum"],
        ]
        optimal_capacities_in_week = [
            req["requirementOnMonday"]["optimal"],
            req["requirementOnTuesday"]["optimal"],
            req["requirementOnWednesday"]["optimal"],
            req["requirementOnThursday"]["optimal"],
            req["requirementOnFriday"]["optimal"],
            req["requirementOnSaturday"]["optimal"],
            req["requirementOnSunday"]["optimal"],
        ]

        for day, min_capacity in enumerate(minimal_capacities_in_week):
            skills_worked = []
            for n in all_nurses:
                skills_worked.append(shifts_with_skills[(n, day, shift, skill)])
            model.Add(sum(skills_worked) >= min_capacity)

        for day, opt_capacity in enumerate(optimal_capacities_in_week):
            skills_worked = []
            for n in all_nurses:
                skills_worked.append(shifts_with_skills[(n, day, shift, skill)])
            model.Add(
                opt_capacity - sum(skills_worked)
                <= insufficient_staffing[(day, shift, skill)]
            )
        return

    def add_shift_succession_reqs(
        self, model, shifts, all_nurses, all_days, all_shifts, num_days, data
    ):
        """Adds hard constraint that disables invalid pairs of succcessive shift types.
        """
        for n in all_nurses:
            last_shift = shift_to_int[
                data["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]

            if last_shift == 2:
                model.Add(
                    0 == shifts[(n, 0, last_shift - 1)] + shifts[(n, 0, last_shift - 2)]
                )
            if last_shift == 3:
                model.Add(
                    0
                    == shifts[(n, 0, last_shift - 1)]
                    + shifts[(n, 0, last_shift - 2)]
                    + shifts[(n, 0, last_shift - 3)]
                )

            for d in range(num_days - 1):
                for s in all_shifts:
                    # if(s == 1):
                    #     model.AddAtMostOne([shifts[(n, d, s)], shifts[(n, d + 1, s - 1)]])
                    if s == 2:
                        model.AddAtMostOne(
                            [
                                shifts[(n, d, s)],
                                shifts[(n, d + 1, s - 1)],
                                shifts[(n, d + 1, s - 2)],
                            ]
                        )
                    if s == 3:
                        model.AddAtMostOne(
                            [
                                shifts[(n, d, s)],
                                shifts[(n, d + 1, s - 1)],
                                shifts[(n, d + 1, s - 2)],
                                shifts[(n, d + 1, s - 3)],
                            ]
                        )
        return

    def add_missing_skill_req(
        self, model, nurses_data, shifts_with_skills, all_days, all_shifts, all_skills
    ):
        """Adds hard constraint that disables nurses working shift with a skill that they do not possess.
        """
        for index, nurse_data in enumerate(nurses_data):
            for sk in all_skills:
                has_skill = False
                for skill in nurse_data["skills"]:
                    if sk == skill_to_int[skill]:
                        has_skill = True
                        break
                if has_skill is False:
                    # print(f"  Nurse {nurse_data['id']} does not have skill {sk}")
                    for d in all_days:
                        for s in all_shifts:
                            model.Add(shifts_with_skills[(index, d, s, sk)] == 0)

        return

    def add_insatisfied_preferences_reqs(
        self,
        model,
        preferences,
        unsatisfied_preferences,
        shifts,
        all_nurses,
        all_days,
        all_shifts,
        all_skills,
    ):
        """Adds the soft constraint that introduces the preferences of nurses for specific assignments/non-assignments.
        """
        for preference in preferences:
            nurse_id = int(preference["nurse"].split("_")[1])
            day_id = day_to_int[preference["day"]]
            shift_id = shift_to_int[preference["shiftType"]]

            if shift_id != shift_to_int["Any"]:
                model.Add(
                    unsatisfied_preferences[(nurse_id, day_id, shift_id)]
                    == shifts[(nurse_id, day_id, shift_id)]
                )
            else:
                for shift in all_shifts:
                    model.Add(
                        unsatisfied_preferences[(nurse_id, day_id, shift)]
                        == shifts[(nurse_id, day_id, shift)]
                    )
        return

    def add_total_working_weekends_soft_constraints(
        self,
        model,
        nurses_data,
        contracts_data,
        history,
        total_working_weekends_over_limit,
        working_weekends,
        all_nurses,
    ):
        """Adds the soft constraint that penilizes more working weekends than the specified maximum.
        """
        for n in all_nurses:
            worked_weekends = []
            worked_weekends_limit = contracts_data[
                contract_to_int[nurses_data[n]["contract"]]
            ]["maximumNumberOfWorkingWeekends"]
            worked_weekends.append(working_weekends[(n)])
            model.Add(
                total_working_weekends_over_limit[(n)]
                >= sum(worked_weekends)
                - worked_weekends_limit
                + history[n]["numberOfWorkingWeekends"]
            )
            model.Add(
                total_working_weekends_over_limit[(n)]
                >= -(
                    sum(worked_weekends)
                    - worked_weekends_limit
                    + history[n]["numberOfWorkingWeekends"]
                )
            )
        return

    def set_objective_function(self, model, basic_CP_vars, soft_CP_vars, data):
        """Sets the objective function contatining all penalties from all enabled constraints.
        """
        all_nurses = data["all_nurses"]
        all_days = data["all_days"]
        all_shifts = data["all_shifts"]
        all_skills = data["all_skills"]

        sc_data = data["sc_data"]

        insufficient_staffing = basic_CP_vars["insufficient_staffing"]

        unsatisfied_preferences = soft_CP_vars["unsatisfied_preferences"]
        total_working_days_over_limit = soft_CP_vars["total_working_days_over_limit"]
        total_incomplete_weekends = soft_CP_vars["total_incomplete_weekends"]
        total_working_weekends_over_limit = soft_CP_vars[
            "total_working_weekends_over_limit"
        ]
        total_working_days_under_limit = soft_CP_vars["total_working_days_under_limit"]
        total_incomplete_weekends = soft_CP_vars["total_incomplete_weekends"]
        violations_of_max_consecutive_working_days_for_nurse = soft_CP_vars[
            "violations_of_max_consecutive_working_days_for_nurse"
        ]
        violations_of_max_consecutive_days_off_for_nurse = soft_CP_vars[
            "violations_of_max_consecutive_days_off_for_nurse"
        ]
        violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type = (
            soft_CP_vars[
                "violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type"
            ]
        )
        violations_of_min_consecutive_days_off = soft_CP_vars[
            "violations_of_min_consecutive_days_off"
        ]
        violations_of_min_consecutive_working_days = soft_CP_vars[
            "violations_of_min_consecutive_working_days"
        ]
        violations_of_min_consecutive_shifts = soft_CP_vars[
            "violations_of_min_consecutive_shifts"
        ]

        summed_violations_of_min_cons_days_off = []
        for n in all_nurses:
            min_consecutive_days_off = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    summed_violations_of_min_cons_days_off.append(
                        dd * violations_of_min_consecutive_days_off[(n, d, dd)]
                    )

        summed_violations_of_min_cons_working_days = []
        for n in all_nurses:
            min_consecutive_wokring_days = sc_data["contracts"][
                contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_wokring_days):
                    summed_violations_of_min_cons_working_days.append(
                        dd * violations_of_min_consecutive_working_days[(n, d, dd)]
                    )

        summed_violations_of_min_cons_shift_type = []
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignments"
                    ]
                    for dd in range(1, min_consecutive_shifts):
                        summed_violations_of_min_cons_shift_type.append(
                            dd * violations_of_min_consecutive_shifts[(n, d, s, dd)]
                        )

        model.Minimize(
            (
                30
                * sum(
                    insufficient_staffing[(d, s, sk)]
                    for d in all_days
                    for s in all_shifts
                    for sk in all_skills
                )
            )
            + (
                10
                * sum(
                    unsatisfied_preferences[(n, d, s)]
                    for n in all_nurses
                    for d in all_days
                    for s in all_shifts
                )
            )
            + (30 * sum(total_working_weekends_over_limit[(n)] for n in all_nurses))
            + (30 * sum(total_incomplete_weekends[(n)] for n in all_nurses))
            + (20 * sum(total_working_days_over_limit[(n)] for n in all_nurses))
            + (20 * sum(total_working_days_under_limit[(n)] for n in all_nurses))
            + (
                30
                * sum(
                    violations_of_max_consecutive_working_days_for_nurse[(n)]
                    for n in all_nurses
                )
            )
            + (
                30
                * sum(
                    violations_of_max_consecutive_days_off_for_nurse[(n)]
                    for n in all_nurses
                )
            )
            + (
                15
                * sum(
                    violations_of_max_consecutive_working_shifts_for_nurse_for_shift_type[
                        (n, s)
                    ]
                    for n in all_nurses
                    for s in all_shifts
                )
            )
            + (30 * sum(summed_violations_of_min_cons_days_off))
            + (30 * sum(summed_violations_of_min_cons_working_days))
            + (15 * sum(summed_violations_of_min_cons_shift_type))
        )
        return

    def save_tmp_results(
        self, results, solver, status, data, basic_CP_vars, soft_CP_vars, week_number
    ):
        """Stores the solution into the results dictionary.

        Args:
            results (dict): dictionary used to store partially computed schedule
            solver : object that contains the computed solution
            status : status of the solution
            data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            week_number (int): number of the computed week
        """
        num_days = data["num_days"]
        num_nurses = data["num_nurses"]
        num_skills = data["num_skills"]
        num_shifts = data["num_shifts"]
        history_data = data["h0_data"]
        working_weekends = soft_CP_vars["working_weekends"]

        shifts_with_skills = basic_CP_vars["shifts_with_skills"]
        working_days = basic_CP_vars["working_days"]
        shifts = basic_CP_vars["shifts"]

        if status != cp_model.FEASIBLE and status != cp_model.OPTIMAL:
            results[(week_number, "status")] = utils.STATUS_FAIL
            return

        results[(week_number, "status")] = utils.STATUS_OK

        for n in range(num_nurses):
            for d in range(num_days):
                for s in range(num_shifts):
                    for sk in range(num_skills):
                        results[(n, d + 7 * week_number, s, sk)] = solver.Value(
                            shifts_with_skills[(n, d, s, sk)]
                        )
                        # if(results[(n, d + 7 * week_number, s, sk)]) == 1:
                history_data["nurseHistory"][n]["numberOfAssignments"] += solver.Value(
                    working_days[(n, d)]
                )
            history_data["nurseHistory"][n]["numberOfWorkingWeekends"] += solver.Value(
                working_weekends[(n)]
            )

            if solver.Value(working_days[(n, 6)]) == 0:
                consecutive_free_days = 1
                d = 5
                while d >= 0 and solver.Value(working_days[(n, d)]) == 0:
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
                while d >= 0 and solver.Value(working_days[(n, d)]) == 1:
                    consecutive_work_days += 1
                    d -= 1
                history_data["nurseHistory"][n][
                    "numberOfConsecutiveWorkingDays"
                ] = consecutive_work_days
                history_data["nurseHistory"][n]["numberOfConsecutiveDaysOff"] = 0

                consecutive_shift = 0
                for s in range(num_shifts):
                    if solver.Value(shifts[(n, 6, s)]) == 1:
                        consecutive_shift = s
                        break
                consecutive_shifts = 1
                for shift_name, shift_id in shift_to_int.items():
                    if shift_id == consecutive_shift:
                        history_data["nurseHistory"][n][
                            "lastAssignedShiftType"
                        ] = shift_name

                d = 5
                while d >= 0 and solver.Value(shifts[(n, d, consecutive_shift)]) == 1:
                    consecutive_shifts += 1
                    d -= 1
                history_data["nurseHistory"][n][
                    "numberOfConsecutiveAssignments"
                ] = consecutive_shifts

        return

    def compute_one_week(self, time_limit_for_week, data, results):
        """Computes a schedule for a week given a time limit and data.

        Args:
            time_limit_for_week (int): time limit for finding a schedule as optimal as possible
            data (dict): dictionary that contains data from input files
            results (dict): dictionary used to store partially computed schedule
        """
        # Creates the model.
        model = cp_model.CpModel()
        week_number = data["h0_data"]["week"]
        # Create ILP variables.
        # shifts, shifts_with_skills, insufficient_staffing = init_cp_vars(model, all_nurses, all_days, all_shifts, all_skills)
        basic_CP_vars = self.init_cp_vars(model, data)

        # Add hard constrains to model
        self.add_hard_constrains(model, basic_CP_vars, data)

        soft_CP_vars = self.init_cp_vars_for_soft_constraints(model, basic_CP_vars, data)

        for req in data["wd_data"]["requirements"]:
            self.add_shift_skill_req(model, req, basic_CP_vars, soft_CP_vars, data)

        self.add_soft_constraints(model, basic_CP_vars, soft_CP_vars, data)

        # Sets objective function
        self.set_objective_function(model, basic_CP_vars, soft_CP_vars, data)

        # Creates the solver and solve.
        solver = cp_model.CpSolver()
        # solver.parameters.linearization_level = 0
        solver.parameters.num_search_workers = 1
        solver.parameters.log_search_progress = False  # Turn off search progress logging
        solver.parameters.log_to_stdout = False        # Turn off all logging to stdout
        # Enumerate all solutions.
        solver.parameters.enumerate_all_solutions = True

        class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
            """Print intermediate solutions."""

            def __init__(self, basic_CP_vars, soft_CP_vars, data, solution_limit):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self._shifts = basic_CP_vars["shifts"]
                self._shifts_with_skills = basic_CP_vars["shifts_with_skills"]
                self._num_nurses = data["num_nurses"]
                self._num_days = data["num_days"]
                self._num_shifts = data["num_shifts"]
                self._solution_count = 0
                self._solution_limit = solution_limit

            def on_solution_callback(self):
                self._solution_count += 1

                # print(f"Solution {self._solution_count} with value: {self.ObjectiveValue()} and time: {self.WallTime()} s")
                if self._solution_count >= self._solution_limit:
                    # print(f"Stop search after {self._solution_limit} solutions")
                    self.StopSearch()

            def solution_count(self):
                return self._solution_count

        # Display the first five solutions.
        solution_limit = 100000
        solution_printer = NursesPartialSolutionPrinter(
            basic_CP_vars, soft_CP_vars, data, solution_limit
        )

        solver.parameters.max_time_in_seconds = time_limit_for_week
        status = solver.Solve(model, solution_printer)

        self.save_tmp_results(
            results, solver, status, data, basic_CP_vars, soft_CP_vars, week_number
        )
        return
