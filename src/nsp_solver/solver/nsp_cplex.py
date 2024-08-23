#!/usr/bin/python

import itertools
import math

import cplex

from nsp_solver.solver.nsp_solver import NSP_solver
from nsp_solver.utils import utils

class CplexSolver(NSP_solver):
    name = 'CPLEX'

    def prepare_help_constants(self, constants, results):
        week_number = constants["h0_data"]["week"]

        constants["wd_data"]["vacations_with_ids"] = list(
            map(lambda x: int(x.split("_")[1]), constants["wd_data"]["vacations"])
        )

        results[(week_number, "status")] = utils.STATUS_FAIL


    def init_ilp_vars(self, model, constants):
        """
        Initializes basic variables for primarly for hard contraints.
        Returns a dictionary 'basic_ILP_vars' containing the names of those variables for further manipulation.
        """

        all_nurses = constants["all_nurses"]
        all_shifts = constants["all_shifts"]
        all_days = constants["all_days"]
        all_skills = constants["all_skills"]
        num_days = constants["num_days"]
        nurses_data = constants["sc_data"]["nurses"]
        contracts_data = constants["sc_data"]["contracts"]

        # Creates shifts variables.
        # shifts[n][d][s]: nurse 'n' works shift 's' on day 'd' if 1 does not work if 0.
        vars_to_add = []
        shifts = []
        for n in all_nurses:
            shifts.append([])
            for d in all_days:
                shifts[n].append([])
                for s in all_shifts:
                    var_name = f"shift_n{n}_d{d}_s{s}"
                    vars_to_add.append(var_name)
                    shifts[n][d].append(var_name)

        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        # Creates working_days variables.
        # shifts[n][d][s]: nurse 'n' works on day 'd' if 1 does not work if 0.
        vars_to_add = []
        working_days = []
        for n in all_nurses:
            working_days.append([])
            for d in all_days:
                var_name = f"work_day_n{n}_d{d}"
                working_days[n].append(var_name)
                vars_to_add.append(var_name)

        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        # Creates shifts_with_skills variables.
        # shifts_with_skills[(n, d, s, sk)]: nurse 'n' works shift 's' on day 'd' with skill 'sk'.
        vars_to_add = []
        shifts_with_skills = []
        for n in all_nurses:
            shifts_with_skills.append([])
            for d in all_days:
                shifts_with_skills[n].append([])
                for s in all_shifts:
                    shifts_with_skills[n][d].append([])
                    for sk in all_skills:
                        var_name = f"shift_with_skill_n{n}_d{d}_s{s}_sk{sk}"
                        vars_to_add.append(var_name)
                        shifts_with_skills[n][d][s].append(var_name)

        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        not_working_days = {}
        for n in all_nurses:
            for d in all_days:
                var_name = f"not_working_day_n{n}_d{d}"
                not_working_days[(n, d)] = var_name
                vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        for n in all_nurses:
            for d in all_days:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [not_working_days[(n, d)], working_days[n][d]], [1, 1]
                        )
                    ],
                    senses=["E"],
                    rhs=[1],
                )

        vars_to_add = []
        not_working_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    var_name = f"not_workingshift_n{n}_d{d}_s{s}"
                    vars_to_add.append(var_name)
                    not_working_shifts[(n, d, s)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                [not_working_shifts[(n, d, s)], shifts[n][d][s]], [1, 1]
                            )
                        ],
                        senses=["E"],
                        rhs=[1],
                    )

        # Vars for each nurse how many days they worked
        vars_to_add = []
        total_assignments = {}
        for n in all_nurses:
            var_name = f"total_assignments_n{n}"
            total_assignments[(n)] = var_name
            vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[num_days + 1] * len(vars_to_add),
            types=["N"] * len(vars_to_add),
        )

        for n in all_nurses:
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [total_assignments[(n)]]
                        + [shifts[n][d][s] for d in all_days for s in all_shifts],
                        [-1]
                        + [1]
                        * len([shifts[n][d][s] for d in all_days for s in all_shifts]),
                    )
                ],
                senses=["E"],
                rhs=[0],
            )

        # Vars for each nurse n indicationg if they were working on weekend this week
        vars_to_add = []
        working_weekends = {}
        for n in all_nurses:
            var_name = f"working_weekends_n{n}"
            working_weekends[(n)] = var_name
            vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        incomplete_weekends = {}
        for n in all_nurses:
            var_name = f"incomplete_weekends_n{n}"
            vars_to_add.append(var_name)
            incomplete_weekends[(n)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        for n in all_nurses:
            isCompleteWeekendRequested = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["completeWeekends"]
            if isCompleteWeekendRequested == 1:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [
                                incomplete_weekends[(n)],
                                working_weekends[(n)],
                                working_days[n][5],
                                working_days[n][6],
                            ],
                            [-1, 2, -1, -1],
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )

        basic_ILP_vars = {}
        basic_ILP_vars["working_days"] = working_days
        basic_ILP_vars["incomplete_weekends"] = incomplete_weekends
        basic_ILP_vars["total_assignments"] = total_assignments
        basic_ILP_vars["working_weekends"] = working_weekends
        basic_ILP_vars["not_working_days"] = not_working_days
        basic_ILP_vars["not_working_shifts"] = not_working_shifts
        basic_ILP_vars["shifts"] = shifts
        basic_ILP_vars["shifts_with_skills"] = shifts_with_skills
        return basic_ILP_vars


    def add_shift_succession_reqs(self, model, basic_ILP_vars, constants):
        """
        Adds hard constraint that disables invalid pairs of succcessive shift types.
        """

        all_nurses = constants["all_nurses"]
        all_shifts = constants["all_shifts"]
        num_days = constants["num_days"]
        shifts = basic_ILP_vars["shifts"]

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                constants["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]
            if last_shift == 2:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [shifts[n][0][last_shift - 1], shifts[n][0][last_shift - 2]],
                            [1] * 2,
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )
            if last_shift == 3:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [
                                shifts[n][0][last_shift - 1],
                                shifts[n][0][last_shift - 2],
                                shifts[n][0][last_shift - 3],
                            ],
                            [1] * 3,
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )

            for d in range(num_days - 1):
                for s in all_shifts:
                    if s == 2:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [
                                        shifts[n][d][s],
                                        shifts[n][d + 1][s - 1],
                                        shifts[n][d + 1][s - 2],
                                    ],
                                    [1] * 3,
                                )
                            ],
                            senses=["L"],
                            rhs=[1],
                        )
                    if s == 3:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [
                                        shifts[n][d][s],
                                        shifts[n][d + 1][s - 1],
                                        shifts[n][d + 1][s - 2],
                                        shifts[n][d + 1][s - 3],
                                    ],
                                    [1] * 4,
                                )
                            ],
                            senses=["L"],
                            rhs=[1],
                        )


    def add_missing_skill_req(self, model, basic_ILP_vars, constants):
        """
        Adds hard constraint that disables nurses working shift with a skill that they do not possess.
        """

        all_shifts = constants["all_shifts"]
        all_days = constants["all_days"]
        all_skills = constants["all_skills"]
        shifts_with_skills = basic_ILP_vars["shifts_with_skills"]
        nurses_data = constants["sc_data"]["nurses"]

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
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair([shifts_with_skills[n][d][s][sk]], [1])
                                ],
                                senses=["E"],
                                rhs=[0],
                            )


    def add_hard_constrains(self, model, basic_ILP_vars, constants):
        """
        Adds all hard constraints to the model.
        """

        if constants["configuration"]["h1"]:
            self.add_max_one_shift_per_day_constraint(model, basic_ILP_vars, constants)

        if constants["configuration"]["h2"]:
            self.add_shift_skill_req_minimal(model, basic_ILP_vars, constants)

        if constants["configuration"]["h3"]:
            self.add_shift_succession_reqs(model, basic_ILP_vars, constants)

        if constants["configuration"]["h4"]:
            self.add_missing_skill_req(model, basic_ILP_vars, constants)

        if constants["configuration"]["h5"]:
            self.add_max_consecutive_work_days_constraint_hard(model, basic_ILP_vars, constants)
            self.add_max_consecutive_work_shifts_constraint_hard(
                model, basic_ILP_vars, constants
            )
            self.add_min_consecutive_work_days_constraint_hard(model, basic_ILP_vars, constants)
            self.add_min_consecutive_shifts_constraint_hard(model, basic_ILP_vars, constants)

        if constants["configuration"]["h6"]:
            self.add_max_consecutive_days_off_constraint_hard(model, basic_ILP_vars, constants)
            self.add_min_consecutive_days_off_constraint_hard(model, basic_ILP_vars, constants)

        if constants["configuration"]["h7"]:
            self.add_max_incomplete_weekends_constraint_hard(model, basic_ILP_vars, constants)

        if constants["configuration"]["h8"]:
            self.add_max_min_total_assignments_constraint_hard(model, basic_ILP_vars, constants)

        if constants["configuration"]["h9"]:
            self.add_min_continuous_free_period_constraint_hard(model, basic_ILP_vars, constants)

        if constants["configuration"]["h10"]:
            self.add_max_one_shift_per_day_exception_constraint_hard(
                model, basic_ILP_vars, constants
            )

        if constants["configuration"]["h11"]:
            self.add_max_shift_of_given_type_constraint_hard(model, basic_ILP_vars, constants)

        if constants["configuration"]["h12"]:
            self.add_vacations_reqs_constraint_hard(model, basic_ILP_vars, constants)


    def add_max_incomplete_weekends_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        incomplete_weekends = basic_ILP_vars["incomplete_weekends"]
        nurses_data = constants["sc_data"]["nurses"]
        contracts_data = constants["sc_data"]["contracts"]

        for n in all_nurses:
            incomplete_weekends_prev = constants["h0_data"]["nurseHistory"][n][
                "numberOfIncompleteWeekends"
            ]
            max_incomplete_weekends = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["maximumNumberOfIncompleteWeekendsHard"]
            model.linear_constraints.add(
                lin_expr=[cplex.SparsePair([incomplete_weekends[(n)]], [1])],
                senses=["L"],
                rhs=[max_incomplete_weekends - incomplete_weekends_prev],
            )


    def add_max_one_shift_per_day_constraint(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_shifts = constants["all_shifts"]
        all_days = constants["all_days"]
        shifts = basic_ILP_vars["shifts"]
        working_days = basic_ILP_vars["working_days"]
        shifts_with_skills = basic_ILP_vars["shifts_with_skills"]

        # Each nurse works at most one shift per day.
        for n in all_nurses:
            for d in all_days:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(shifts[n][d][:], [1] * len(shifts[n][d][:]))
                    ],
                    senses=["L"],
                    rhs=[1],
                )

        # Each nurse works at most one skill per shift.
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                shifts_with_skills[n][d][s][:],
                                [1] * len(shifts_with_skills[n][d][s][:]),
                            )
                        ],
                        senses=["L"],
                        rhs=[1],
                    )

        # If nurse is working with skill that shift, she is working that shift.
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                [shifts[n][d][s]] + shifts_with_skills[n][d][s][:],
                                [-1] + [1] * len(shifts_with_skills[n][d][s][:]),
                            )
                        ],
                        senses=["E"],
                        rhs=[0],
                    )

        # If nurse is working with a shift, she is working that day.
        for n in all_nurses:
            for d in all_days:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [working_days[n][d]] + shifts[n][d][:],
                            [-1] + [1] * len(shifts[n][d][:]),
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )


    def add_max_shift_of_given_type_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        num_days = constants["num_days"]
        shifts = basic_ILP_vars["shifts"]

        for n in all_nurses:
            already_assigned = constants["h0_data"]["nurseHistory"][n][
                "numbersOfAssignedRestrictedShiftTypes"
            ]
            for restriction in constants["sc_data"]["nurses"][n]["restrictions"]:
                shift_id = utils.shift_to_int[restriction["type"]]
                limit = restriction["limit"]
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [shifts[n][d][shift_id] for d in all_days], [1] * num_days
                        )
                    ],
                    senses=["L"],
                    rhs=[limit - already_assigned[shift_id]["numberOfAssignments"]],
                )


    def add_max_one_shift_per_day_exception_constraint_hard(
        self, model, basic_ILP_vars, constants
    ):
        all_nurses = constants["all_nurses"]
        all_shifts = constants["all_shifts"]
        all_days = constants["all_days"]
        num_shifts = constants["num_shifts"]
        shifts = basic_ILP_vars["shifts"]
        working_days = basic_ILP_vars["working_days"]
        shifts_with_skills = basic_ILP_vars["shifts_with_skills"]

        # Each nurse works at most one shift per day with an exception early + night.
        for n in all_nurses:
            for d in all_days:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            shifts[n][d][0: (num_shifts - 1)], [1] * (num_shifts - 1)
                        )
                    ],
                    senses=["L"],
                    rhs=[1],
                )
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(shifts[n][d][1:num_shifts], [1] * (num_shifts - 1))
                    ],
                    senses=["L"],
                    rhs=[1],
                )

        # If nurse is working with a shift, she is working that day.
        for n in all_nurses:
            for d in all_days:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [working_days[n][d]] + shifts[n][d][:],
                            [-4] + [1] * len(shifts[n][d][:]),
                        )
                    ],
                    senses=["L"],
                    rhs=[0],
                )
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [working_days[n][d]] + shifts[n][d][:],
                            [1] + [-2] * len(shifts[n][d][:]),
                        )
                    ],
                    senses=["L"],
                    rhs=[0],
                )

        # Each nurse works at most one skill per shift.
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                shifts_with_skills[n][d][s][:],
                                [1] * len(shifts_with_skills[n][d][s][:]),
                            )
                        ],
                        senses=["L"],
                        rhs=[1],
                    )

        # If nurse is working with skill that shift, she is working that shift.
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                [shifts[n][d][s]] + shifts_with_skills[n][d][s][:],
                                [-1] + [1] * len(shifts_with_skills[n][d][s][:]),
                            )
                        ],
                        senses=["E"],
                        rhs=[0],
                    )


    def add_vacations_reqs_constraint_hard(self, model, basic_ILP_vars, constants):
        wd_data = constants["wd_data"]
        working_days = basic_ILP_vars["working_days"]

        for nurse_id in wd_data["vacations_with_ids"]:
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        working_days[nurse_id][:], [1] * len(working_days[nurse_id][:])
                    )
                ],
                senses=["E"],
                rhs=[0],
            )


    def add_shift_skill_req_minimal(self, model, basic_ILP_vars, constants):
        """
        Adds hard constraint that dictates minimal number of nurses in a shift working with specific skill.
        """

        all_nurses = constants["all_nurses"]
        shifts_with_skills = basic_ILP_vars["shifts_with_skills"]

        for req in constants["wd_data"]["requirements"]:

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
                skills_worked = []
                for n in all_nurses:
                    skills_worked.append(shifts_with_skills[n][d][s][sk])
                model.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(skills_worked, [1] * len(skills_worked))],
                    senses=["G"],
                    rhs=[min_capacity],
                )


    def add_min_continuous_free_period_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        num_days = constants["num_days"]
        working_days = basic_ILP_vars["working_days"]

        for n in all_nurses:
            nurses_data = constants["sc_data"]["nurses"]
            contracts_data = constants["sc_data"]["contracts"]
            min_free_period = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["minimalFreePeriod"]

            vars_to_add = []
            free_periods = {}
            for d in range(num_days - min_free_period + 1):
                var_name = f"free_period_of_{min_free_period}_days_n{n}_d{d}"
                vars_to_add.append(var_name)
                free_periods[(n, d)] = var_name
            model.variables.add(
                names=vars_to_add,
                lb=[0] * len(vars_to_add),
                ub=[1] * len(vars_to_add),
                types=["N"] * len(vars_to_add),
            )

            for d in range(num_days - min_free_period + 1):
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [free_periods[(n, d)]]
                            + working_days[n][d: d + min_free_period],
                            [1] + [1] * min_free_period,
                        )
                    ],
                    senses=["G"],
                    rhs=[0],
                )

                for dd in range(d, d + min_free_period):
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                [free_periods[(n, d)]] + [working_days[n][dd]],
                                [1] + [1],
                            )
                        ],
                        senses=["L"],
                        rhs=[1],
                    )

            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [
                            free_periods[(n, d)]
                            for d in range(num_days - min_free_period + 1)
                        ],
                        [1] * (num_days - min_free_period + 1),
                    )
                ],
                senses=["G"],
                rhs=[1],
            )


    def add_max_min_total_assignments_constraint_hard(self, model, basic_ILP_vars, constants):
        nurses_data = constants["sc_data"]["nurses"]
        contracts_data = constants["sc_data"]["contracts"]
        num_weeks = constants["num_weeks"]
        total_assignments = basic_ILP_vars["total_assignments"]
        all_nurses = constants["all_nurses"]
        h0_data = constants["h0_data"]
        week_number = constants["h0_data"]["week"]

        for n in all_nurses:
            if constants["configuration"]["h12"] and (
                n in constants["wd_data"]["vacations_with_ids"]
            ):
                continue

            worked_days_in_previous_weeks = h0_data["nurseHistory"][n][
                "numberOfAssignments"
            ]
            upper_limit = math.ceil(
                contracts_data[utils.contract_to_int[nurses_data[n]["contract"]]][
                    "maximumNumberOfAssignmentsHard"
                ]
                * ((week_number + 1) / num_weeks)
            )
            lower_limit = contracts_data[utils.contract_to_int[nurses_data[n]["contract"]]][
                "minimumNumberOfAssignmentsHard"
            ]

            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [total_assignments[(n)]],
                        [1],
                    )
                ],
                senses=["L"],
                rhs=[upper_limit - worked_days_in_previous_weeks],
            )

            if (week_number + 1) == num_weeks:
                model.linear_constraints.add(
                    lin_expr=[cplex.SparsePair([total_assignments[(n)]], [1])],
                    senses=["G"],
                    rhs=[lower_limit - worked_days_in_previous_weeks],
                )


    def init_ilp_vars_for_soft_constraints(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_shifts = constants["all_shifts"]
        all_skills = constants["all_skills"]
        all_days = constants["all_days"]
        num_weeks = constants["num_weeks"]
        sc_data = constants["sc_data"]

        # Creates insufficient staffing variables.
        # shifts[(d,s,sk)]: number of nurses under optimal number for day d shift s and skill sk
        vars_to_add = []
        insufficient_staffing = {}
        for d in all_days:
            for s in all_shifts:
                for sk in all_skills:
                    var_name = f"insufficient_staffing_d{d}_s{s}_sk{sk}"
                    vars_to_add.append(var_name)
                    insufficient_staffing[(d, s, sk)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[10] * len(vars_to_add),
            types=["N"] * len(vars_to_add),
        )

        # Creates unsatisfied preferences variables.
        # unsatisfied_preferences_n{n}_d{d}_s{s} of nurse n for day d and shift s
        vars_to_add = []
        unsatisfied_preferences = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    var_name = f"unsatisfied_preferences_n{n}_d{d}_s{s}"
                    vars_to_add.append(var_name)
                    unsatisfied_preferences[(n, d, s)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        # Vars for each nurse n indicationg if how many weekends were they working up to this week over the limit
        vars_to_add = []
        total_working_weekends_over_limit = {}
        for n in all_nurses:
            var_name = f"total_working_weekends_over_limit_n{n}"
            total_working_weekends_over_limit[(n)] = var_name
            vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[num_weeks] * len(vars_to_add),
            types=["N"] * len(vars_to_add),
        )

        vars_to_add = []
        total_assignments_over_limit = {}
        total_assignments_under_limit = {}
        for n in all_nurses:
            var_name1, var_name2 = (
                f"total_assignments_over_limit_n{n}",
                f"total_assignments_under_limit_n{n}",
            )
            total_assignments_over_limit[(n)] = var_name1
            total_assignments_under_limit[(n)] = var_name2
            vars_to_add.append(var_name1)
            vars_to_add.append(var_name2)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[7] * len(vars_to_add),
            types=["N"] * len(vars_to_add),
        )

        vars_to_add = []
        violations_of_max_consecutive_working_days = {}
        for n in all_nurses:
            for d in all_days:
                var_name = f"violations_of_max_consecutive_working_days_n{n}_d{d}"
                vars_to_add.append(var_name)
                violations_of_max_consecutive_working_days[(n, d)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        violations_of_max_consecutive_working_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    var_name = (
                        f"violations_of_max_consecutive_working_shifts_n{n}_d{d}_s{s}"
                    )
                    violations_of_max_consecutive_working_shifts[(n, d, s)] = var_name
                    vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        violations_of_max_consecutive_days_off = {}
        for n in all_nurses:
            for d in all_days:
                var_name = f"violations_of_max_consecutive_days_off_n{n}_d{d}"
                vars_to_add.append(var_name)
                violations_of_max_consecutive_days_off[(n, d)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        violations_of_min_consecutive_days_off = {}
        for n in all_nurses:
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    var_name = f"violations_of_min_consecutive_days_off_n{n}_d{d}_dd{dd}"
                    vars_to_add.append(var_name)
                    violations_of_min_consecutive_days_off[(n, d, dd)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        violations_of_min_consecutive_working_days = {}
        for n in all_nurses:
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    var_name = (
                        f"violations_of_min_consecutive_working_days_n{n}_d{d}_dd{dd}"
                    )
                    vars_to_add.append(var_name)
                    violations_of_min_consecutive_working_days[(n, d, dd)] = var_name
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        violations_of_min_consecutive_working_shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_working_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignments"
                    ]
                    for dd in range(1, min_consecutive_working_shifts):
                        var_name = f"violations_of_min_consecutive_working_shifts_n{n}_d{d}_s{s}_dd{dd}"
                        violations_of_min_consecutive_working_shifts[(n, d, s, dd)] = (
                            var_name
                        )
                        vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[1] * len(vars_to_add),
            types=["B"] * len(vars_to_add),
        )

        vars_to_add = []
        total_assignments_with_if_needed_skill = {}
        for n in all_nurses:
            var_name = f"total_assignments_with_if_needed_skill_n{n}"
            total_assignments_with_if_needed_skill[(n)] = var_name
            vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[28] * len(vars_to_add),
            types=["N"] * len(vars_to_add),
        )

        vars_to_add = []
        total_unsatisfied_overtime = {}
        for n in all_nurses:
            var_name = f"total_unsatisfied_overtime_n{n}"
            total_unsatisfied_overtime[(n)] = var_name
            vars_to_add.append(var_name)
        model.variables.add(
            names=vars_to_add,
            lb=[0] * len(vars_to_add),
            ub=[7] * len(vars_to_add),
            types=["N"] * len(vars_to_add),
        )

        soft_ILP_vars = {}
        soft_ILP_vars["insufficient_staffing"] = insufficient_staffing
        soft_ILP_vars["total_unsatisfied_overtime"] = total_unsatisfied_overtime
        soft_ILP_vars["total_assignments_with_if_needed_skill"] = (
            total_assignments_with_if_needed_skill
        )
        soft_ILP_vars["unsatisfied_preferences"] = unsatisfied_preferences
        soft_ILP_vars["total_working_weekends_over_limit"] = (
            total_working_weekends_over_limit
        )
        soft_ILP_vars["total_assignments_over_limit"] = total_assignments_over_limit
        soft_ILP_vars["total_assignments_under_limit"] = total_assignments_under_limit
        soft_ILP_vars["violations_of_max_consecutive_working_days"] = (
            violations_of_max_consecutive_working_days
        )
        soft_ILP_vars["violations_of_max_consecutive_days_off"] = (
            violations_of_max_consecutive_days_off
        )
        soft_ILP_vars["violations_of_max_consecutive_working_shifts"] = (
            violations_of_max_consecutive_working_shifts
        )
        soft_ILP_vars["violations_of_min_consecutive_working_days"] = (
            violations_of_min_consecutive_working_days
        )
        soft_ILP_vars["violations_of_min_consecutive_days_off"] = (
            violations_of_min_consecutive_days_off
        )
        soft_ILP_vars["violations_of_min_consecutive_working_shifts"] = (
            violations_of_min_consecutive_working_shifts
        )

        return soft_ILP_vars


    def add_shift_skill_req_optimal_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        all_nurses = constants["all_nurses"]
        shifts_with_skills = basic_ILP_vars["shifts_with_skills"]
        insufficient_staffing = soft_ILP_vars["insufficient_staffing"]

        wd_data = constants["wd_data"]

        for req in wd_data["requirements"]:
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
                skills_worked = []
                for n in all_nurses:
                    skills_worked.append(shifts_with_skills[n][d][s][sk])
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [insufficient_staffing[(d, s, sk)]] + skills_worked,
                            [1] + [1] * len(skills_worked),
                        )
                    ],
                    senses=["G"],
                    rhs=[opt_capacity],
                )


    def add_insatisfied_preferences_reqs_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        unsatisfied_preferences = soft_ILP_vars["unsatisfied_preferences"]
        shifts = basic_ILP_vars["shifts"]
        working_days = basic_ILP_vars["working_days"]
        wd_data = constants["wd_data"]

        for preference in wd_data["shiftOffRequests"]:
            nurse_id = int(preference["nurse"].split("_")[1])
            day_id = utils.day_to_int[preference["day"]]
            shift_id = utils.shift_to_int[preference["shiftType"]]

            if shift_id != utils.shift_to_int["Any"]:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [
                                unsatisfied_preferences[(nurse_id, day_id, shift_id)],
                                shifts[nurse_id][day_id][shift_id],
                            ],
                            [1, -1],
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )
            else:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [
                                unsatisfied_preferences[(nurse_id, day_id, 0)],
                                working_days[nurse_id][day_id],
                            ],
                            [1, -1],
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )

        # for preference in wd_data["shiftOnRequests"]:
        #     nurse_id = int(preference["nurse"].split("_")[1])
        #     day_id = day_to_int[preference["day"]]
        #     shift_id = utils.shift_to_int[preference["shiftType"]]

        #     if shift_id != utils.shift_to_int["Any"]:
        #         model.linear_constraints.add(
        #             lin_expr=[
        #                 cplex.SparsePair(
        #                     [
        #                         unsatisfied_preferences[(nurse_id, day_id, shift_id)],
        #                         shifts[nurse_id][day_id][shift_id],
        #                     ],
        #                     [1, 1],
        #                 )
        #             ],
        #             senses=["E"],
        #             rhs=[1],
        #         )


    def add_total_working_weekends_constraints_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        week_number = constants["h0_data"]["week"]
        sc_data = constants["sc_data"]
        h0_data = constants["h0_data"]
        total_working_weekends_over_limit = soft_ILP_vars[
            "total_working_weekends_over_limit"
        ]
        working_weekends = basic_ILP_vars["working_weekends"]

        all_nurses = constants["all_nurses"]
        num_weeks = constants["num_weeks"]
        working_days = basic_ILP_vars["working_days"]

        for n in all_nurses:
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair([working_weekends[(n)], working_days[n][5]], [1, -1])
                ],
                senses=["G"],
                rhs=[0],
            )
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair([working_weekends[(n)], working_days[n][6]], [1, -1])
                ],
                senses=["G"],
                rhs=[0],
            )

        for n in all_nurses:
            # worked_weekends_limit_for_this_week = sc_data["contracts"][utils.contract_to_int[sc_data["nurses"][n]["contract"]]]["maximumNumberOfWorkingWeekends"]
            worked_weekends_limit_for_this_week = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfWorkingWeekends"] * ((week_number + 1) / num_weeks)
            worked_weekends_in_previous_weeks = h0_data["nurseHistory"][n][
                "numberOfWorkingWeekends"
            ]
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [total_working_weekends_over_limit[(n)], working_weekends[(n)]],
                        [-1, 1],
                    )
                ],
                senses=["L"],
                rhs=[
                    worked_weekends_limit_for_this_week - worked_weekends_in_previous_weeks
                ],
            )
            # worked_weekends.append(working_weekends[(n)])
            # model.Add(total_working_weekends_over_limit[(n)] >= sum(worked_weekends) - worked_weekends_limit + worked_weekends_in_previous_weeks)
            # model.Add(total_working_weekends_over_limit[(n)] >= -(sum(worked_weekends) - worked_weekends_limit + worked_weekends_in_previous_weeks))


    def add_incomplete_weekends_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        nurses_data = constants["sc_data"]["nurses"]
        contracts_data = constants["sc_data"]["contracts"]
        incomplete_weekends = basic_ILP_vars["incomplete_weekends"]
        working_weekends = basic_ILP_vars["working_weekends"]
        working_days = basic_ILP_vars["working_days"]
        all_nurses = constants["all_nurses"]

        for n in all_nurses:
            isCompleteWeekendRequested = contracts_data[
                utils.contract_to_int[nurses_data[n]["contract"]]
            ]["completeWeekends"]
            if isCompleteWeekendRequested == 1:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [
                                incomplete_weekends[(n)],
                                working_weekends[(n)],
                                working_days[n][5],
                                working_days[n][6],
                            ],
                            [-1, 2, -1, -1],
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )


    def add_total_assignments_out_of_bounds_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        nurses_data = constants["sc_data"]["nurses"]
        contracts_data = constants["sc_data"]["contracts"]
        total_assignments = basic_ILP_vars["total_assignments"]
        total_assignments_over_limit = soft_ILP_vars["total_assignments_over_limit"]
        total_assignments_under_limit = soft_ILP_vars["total_assignments_under_limit"]
        all_nurses = constants["all_nurses"]
        num_weeks = constants["num_weeks"]
        h0_data = constants["h0_data"]
        week_number = constants["h0_data"]["week"]

        for n in all_nurses:
            if constants["configuration"]["h12"] and (
                n in constants["wd_data"]["vacations_with_ids"]
            ):
                continue

            if constants["configuration"]["s9"] and (nurses_data[n]["wantedOvertime"] > 0):
                continue

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
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [total_assignments_over_limit[(n)], total_assignments[(n)]],
                        [-1, 1],
                    )
                ],
                senses=["L"],
                rhs=[upper_limit - worked_days_in_previous_weeks],
            )
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [total_assignments_under_limit[(n)], total_assignments[(n)]],
                        [1, 1],
                    )
                ],
                senses=["G"],
                rhs=[lower_limit - worked_days_in_previous_weeks],
            )


    def add_max_consecutive_work_days_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        violations_of_max_consecutive_working_days = soft_ILP_vars[
            "violations_of_max_consecutive_working_days"
        ]
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                [violations_of_max_consecutive_working_days[(n, d)]]
                                + working_days[n][d - max_consecutive_working_days: d + 1],
                                [-1] + [1] * (max_consecutive_working_days + 1),
                            )
                        ],
                        senses=["L"],
                        rhs=[max_consecutive_working_days],
                    )
                else:
                    if (
                        consecutive_working_days_prev_week
                        >= max_consecutive_working_days - d
                    ):
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [violations_of_max_consecutive_working_days[(n, d)]]
                                    + working_days[n][0: d + 1],
                                    [-1] + [1] * (d + 1),
                                )
                            ],
                            senses=["L"],
                            rhs=[d],
                        )


    def add_min_consecutive_work_days_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        violations_of_min_consecutive_working_days = soft_ILP_vars[
            "violations_of_min_consecutive_working_days"
        ]
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]
        not_working_days = basic_ILP_vars["not_working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDays"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    if (d - dd) > 0:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [violations_of_min_consecutive_working_days[(n, d, dd)]]
                                    + [not_working_days[(n, d)]]
                                    + working_days[n][d - dd: d]
                                    + [not_working_days[(n, d - dd - 1)]],
                                    [-1] + [1] * (dd + 2),
                                )
                            ],
                            senses=["L"],
                            rhs=[dd + 1],
                        )
                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [
                                            violations_of_min_consecutive_working_days[
                                                (n, d, dd)
                                            ]
                                        ]
                                        + [not_working_days[(n, d)]]
                                        + working_days[n][0:d],
                                        [-1] + [1] * (d + 1),
                                    )
                                ],
                                senses=["L"],
                                rhs=[d],
                            )


    def add_min_consecutive_work_days_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]
        not_working_days = basic_ILP_vars["not_working_days"]

        for n in all_nurses:
            if constants["configuration"]["h12"] and (
                n in constants["wd_data"]["vacations_with_ids"]
            ):
                continue

            consecutive_working_days_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            min_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveWorkingDaysHard"]
            for d in all_days:
                for dd in range(1, min_consecutive_working_days):
                    if (d - dd) > 0:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [not_working_days[(n, d)]]
                                    + working_days[n][d - dd: d]
                                    + [not_working_days[(n, d - dd - 1)]],
                                    [1] * (dd + 2),
                                )
                            ],
                            senses=["L"],
                            rhs=[dd + 1],
                        )
                    else:
                        if consecutive_working_days_prev_week == dd - d:
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [not_working_days[(n, d)]] + working_days[n][0:d],
                                        [1] * (d + 1),
                                    )
                                ],
                                senses=["L"],
                                rhs=[d],
                            )


    def add_min_consecutive_shifts_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        violations_of_min_consecutive_working_shifts = soft_ILP_vars[
            "violations_of_min_consecutive_working_shifts"
        ]
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        all_shifts = constants["all_shifts"]
        sc_data = constants["sc_data"]
        shifts = basic_ILP_vars["shifts"]
        not_working_shifts = basic_ILP_vars["not_working_shifts"]

        for n in all_nurses:
            consecutive_working_shifts_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveAssignments"
            ]
            lastAssignedShiftType = constants["h0_data"]["nurseHistory"][n][
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
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [
                                            violations_of_min_consecutive_working_shifts[
                                                (n, d, s, dd)
                                            ]
                                        ]
                                        + [not_working_shifts[(n, d, s)]]
                                        + list(
                                            (shifts[n][ddd][s]) for ddd in range(d - dd, d)
                                        )
                                        + [not_working_shifts[(n, d - dd - 1, s)]],
                                        [-1] + [1] * (dd + 2),
                                    )
                                ],
                                senses=["L"],
                                rhs=[dd + 1],
                            )
                        else:
                            if (consecutive_working_shifts_prev_week == dd - d) and (
                                lastShittTypeAsInt == s
                            ):
                                model.linear_constraints.add(
                                    lin_expr=[
                                        cplex.SparsePair(
                                            [
                                                violations_of_min_consecutive_working_shifts[
                                                    (n, d, s, dd)
                                                ]
                                            ]
                                            + [not_working_shifts[(n, d, s)]]
                                            + list((shifts[n][ddd][s]) for ddd in range(d)),
                                            [-1] + [1] * (d + 1),
                                        )
                                    ],
                                    senses=["L"],
                                    rhs=[d],
                                )


    def add_min_consecutive_shifts_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        all_shifts = constants["all_shifts"]
        sc_data = constants["sc_data"]
        shifts = basic_ILP_vars["shifts"]
        not_working_shifts = basic_ILP_vars["not_working_shifts"]

        for n in all_nurses:
            if constants["configuration"]["h12"] and (
                n in constants["wd_data"]["vacations_with_ids"]
            ):
                continue
            consecutive_working_shifts_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveAssignments"
            ]
            lastAssignedShiftType = constants["h0_data"]["nurseHistory"][n][
                "lastAssignedShiftType"
            ]
            lastShittTypeAsInt = utils.shift_to_int[lastAssignedShiftType]
            for d in all_days:
                for s in all_shifts:
                    min_consecutive_shifts = sc_data["shiftTypes"][s][
                        "minimumNumberOfConsecutiveAssignmentsHard"
                    ]
                    for dd in range(1, min_consecutive_shifts):
                        if (d - dd) > 0:
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [not_working_shifts[(n, d, s)]]
                                        + list(
                                            (shifts[n][ddd][s]) for ddd in range(d - dd, d)
                                        )
                                        + [not_working_shifts[(n, d - dd - 1, s)]],
                                        [1] * (dd + 2),
                                    )
                                ],
                                senses=["L"],
                                rhs=[dd + 1],
                            )
                        else:
                            if (consecutive_working_shifts_prev_week == dd - d) and (
                                lastShittTypeAsInt == s
                                or consecutive_working_shifts_prev_week == 0
                            ):
                                model.linear_constraints.add(
                                    lin_expr=[
                                        cplex.SparsePair(
                                            [not_working_shifts[(n, d, s)]]
                                            + list((shifts[n][ddd][s]) for ddd in range(d)),
                                            [1] * (d + 1),
                                        )
                                    ],
                                    senses=["L"],
                                    rhs=[d],
                                )
                        if (d - dd) == 0 and lastShittTypeAsInt != s:
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [not_working_shifts[(n, d, s)]]
                                        + list(
                                            (shifts[n][ddd][s]) for ddd in range(d - dd, d)
                                        ),
                                        # + [not_working_shifts[(n, d - dd - 1, s)]],
                                        [1] * (dd + 1),
                                    )
                                ],
                                senses=["L"],
                                rhs=[dd],
                            )


    def add_min_consecutive_days_off_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        violations_of_min_consecutive_days_off = soft_ILP_vars[
            "violations_of_min_consecutive_days_off"
        ]
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]
        not_working_days = basic_ILP_vars["not_working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    if (d - dd) > 0:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [violations_of_min_consecutive_days_off[(n, d, dd)]]
                                    + [working_days[n][d]]
                                    + list(
                                        not_working_days[(n, ddd)]
                                        for ddd in range(d - dd, d)
                                    )
                                    + [working_days[n][d - dd - 1]],
                                    [-1] + [1] * (dd + 2),
                                )
                            ],
                            senses=["L"],
                            rhs=[dd + 1],
                        )
                    else:
                        if consecutive_working_days_prev_week == d - dd:
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [violations_of_min_consecutive_days_off[(n, d, dd)]]
                                        + [working_days[n][d]]
                                        + list(
                                            not_working_days[(n, ddd)]
                                            for ddd in range(0, d)
                                        ),
                                        [-1] + [1] * (d + 1),
                                    )
                                ],
                                senses=["L"],
                                rhs=[d],
                            )


    def add_min_consecutive_days_off_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]
        not_working_days = basic_ILP_vars["not_working_days"]

        for n in all_nurses:
            if constants["configuration"]["h12"] and (
                n in constants["wd_data"]["vacations_with_ids"]
            ):
                continue
            consecutive_days_off_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            min_consecutive_days_off = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["minimumNumberOfConsecutiveDaysOffHard"]
            for d in all_days:
                for dd in range(1, min_consecutive_days_off):
                    if (d - dd) > 0:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [working_days[n][d]]
                                    + list(
                                        not_working_days[(n, ddd)]
                                        for ddd in range(d - dd, d)
                                    )
                                    + [working_days[n][d - dd - 1]],
                                    [1] * (dd + 2),
                                )
                            ],
                            senses=["L"],
                            rhs=[dd + 1],
                        )
                    else:
                        if consecutive_days_off_prev_week == d - dd:
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [working_days[n][d]]
                                        + list(
                                            not_working_days[(n, ddd)]
                                            for ddd in range(0, d)
                                        ),
                                        [1] * (d + 1),
                                    )
                                ],
                                senses=["L"],
                                rhs=[d],
                            )


    def add_max_consecutive_work_shifts_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        violations_of_max_consecutive_working_shifts = soft_ILP_vars[
            "violations_of_max_consecutive_working_shifts"
        ]
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        all_shifts = constants["all_shifts"]
        sc_data = constants["sc_data"]
        shifts = basic_ILP_vars["shifts"]

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                constants["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]
            consecutive_shifts_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveAssignments"
            ]
            for s in all_shifts:
                max_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "maximumNumberOfConsecutiveAssignments"
                ]
                for d in all_days:
                    if d > max_consecutive_working_shifts:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [
                                        violations_of_max_consecutive_working_shifts[
                                            (n, d, s)
                                        ]
                                    ]
                                    + list(
                                        shifts[n][d - dd][s]
                                        for dd in range(1 + max_consecutive_working_shifts)
                                    ),
                                    [-1] + [1] * (max_consecutive_working_shifts + 1),
                                )
                            ],
                            senses=["L"],
                            rhs=[max_consecutive_working_shifts],
                        )
                    else:
                        if (last_shift == s) and (
                            consecutive_shifts_prev_week
                            >= max_consecutive_working_shifts - d
                        ):
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        [
                                            violations_of_max_consecutive_working_shifts[
                                                (n, d, s)
                                            ]
                                        ]
                                        + list(shifts[n][dd][s] for dd in range(d + 1)),
                                        [-1] + [1] * (d + 1),
                                    )
                                ],
                                senses=["L"],
                                rhs=[d],
                            )


    def add_max_consecutive_days_off_constraint_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        violations_of_max_consecutive_days_off = soft_ILP_vars[
            "violations_of_max_consecutive_days_off"
        ]
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]

        for n in all_nurses:
            consecutive_days_off_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveDaysOff"]
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                [violations_of_max_consecutive_days_off[(n, d)]]
                                + working_days[n][d - max_consecutive_working_days: d + 1],
                                [1] + [1] * (max_consecutive_working_days + 1),
                            )
                        ],
                        senses=["G"],
                        rhs=[1],
                    )
                else:
                    if consecutive_days_off_prev_week >= max_consecutive_working_days - d:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    [violations_of_max_consecutive_days_off[(n, d)]]
                                    + working_days[n][0: d + 1],
                                    [1] + [1] * (d + 1),
                                )
                            ],
                            senses=["G"],
                            rhs=[1],
                        )


    def add_max_consecutive_work_shifts_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        all_shifts = constants["all_shifts"]
        sc_data = constants["sc_data"]
        shifts = basic_ILP_vars["shifts"]

        for n in all_nurses:
            last_shift = utils.shift_to_int[
                constants["h0_data"]["nurseHistory"][n]["lastAssignedShiftType"]
            ]
            consecutive_shifts_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveAssignments"
            ]
            for s in all_shifts:
                max_consecutive_working_shifts = sc_data["shiftTypes"][s][
                    "maximumNumberOfConsecutiveAssignmentsHard"
                ]
                for d in all_days:
                    if d > max_consecutive_working_shifts:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(
                                    list(
                                        shifts[n][d - dd][s]
                                        for dd in range(1 + max_consecutive_working_shifts)
                                    ),
                                    [1] * (max_consecutive_working_shifts + 1),
                                )
                            ],
                            senses=["L"],
                            rhs=[max_consecutive_working_shifts],
                        )
                    else:
                        if (last_shift == s) and (
                            consecutive_shifts_prev_week
                            >= max_consecutive_working_shifts - d
                        ):
                            model.linear_constraints.add(
                                lin_expr=[
                                    cplex.SparsePair(
                                        list(shifts[n][dd][s] for dd in range(d + 1)),
                                        [1] * (d + 1),
                                    )
                                ],
                                senses=["L"],
                                rhs=[d],
                            )


    def add_max_consecutive_work_days_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]

        for n in all_nurses:
            consecutive_working_days_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveWorkingDays"
            ]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveWorkingDaysHard"]
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                working_days[n][d - max_consecutive_working_days: d + 1],
                                [1] * (max_consecutive_working_days + 1),
                            )
                        ],
                        senses=["L"],
                        rhs=[max_consecutive_working_days],
                    )
                else:
                    if (
                        consecutive_working_days_prev_week
                        >= max_consecutive_working_days - d
                    ):
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(working_days[n][0: d + 1], [1] * (d + 1))
                            ],
                            senses=["L"],
                            rhs=[d],
                        )


    def add_max_consecutive_days_off_constraint_hard(self, model, basic_ILP_vars, constants):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        sc_data = constants["sc_data"]
        working_days = basic_ILP_vars["working_days"]

        for n in all_nurses:
            if constants["configuration"]["h12"] and (
                n in constants["wd_data"]["vacations_with_ids"]
            ):
                continue

            consecutive_days_off_prev_week = constants["h0_data"]["nurseHistory"][n][
                "numberOfConsecutiveDaysOff"
            ]
            max_consecutive_working_days = sc_data["contracts"][
                utils.contract_to_int[sc_data["nurses"][n]["contract"]]
            ]["maximumNumberOfConsecutiveDaysOffHard"]
            for d in all_days:
                if d > max_consecutive_working_days:
                    model.linear_constraints.add(
                        lin_expr=[
                            cplex.SparsePair(
                                working_days[n][d - max_consecutive_working_days: d + 1],
                                [1] * (max_consecutive_working_days + 1),
                            )
                        ],
                        senses=["G"],
                        rhs=[1],
                    )
                else:
                    if consecutive_days_off_prev_week >= max_consecutive_working_days - d:
                        model.linear_constraints.add(
                            lin_expr=[
                                cplex.SparsePair(working_days[n][0: d + 1], [1] * (d + 1))
                            ],
                            senses=["G"],
                            rhs=[1],
                        )


    def add_total_assignments_with_if_needed_skill_constraints_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        all_nurses = constants["all_nurses"]
        all_days = constants["all_days"]
        all_shifts = constants["all_shifts"]
        nurses_data = constants["sc_data"]["nurses"]

        shifts_with_skills = basic_ILP_vars["shifts_with_skills"]
        total_assignments_with_if_needed_skill = soft_ILP_vars[
            "total_assignments_with_if_needed_skill"
        ]

        for n in all_nurses:
            if len(nurses_data[n]["skillsIfNeeded"]) > 0:
                model.linear_constraints.add(
                    lin_expr=[
                        cplex.SparsePair(
                            [total_assignments_with_if_needed_skill[(n)]]
                            + [
                                shifts_with_skills[n][d][s][utils.skill_to_int[sk]]
                                for sk in nurses_data[n]["skillsIfNeeded"]
                                for s in all_shifts
                                for d in all_days
                            ],
                            [-1]
                            + [1]
                            * len(
                                [
                                    shifts_with_skills[n][d][s][utils.skill_to_int[sk]]
                                    for sk in nurses_data[n]["skillsIfNeeded"]
                                    for s in all_shifts
                                    for d in all_days
                                ]
                            ),
                        )
                    ],
                    senses=["E"],
                    rhs=[0],
                )


    def add_total_unsatisfied_overtime_constraints_soft(
        self, model, basic_ILP_vars, soft_ILP_vars, constants
    ):
        nurses_data = constants["sc_data"]["nurses"]
        total_assignments = basic_ILP_vars["total_assignments"]
        contracts_data = constants["sc_data"]["contracts"]
        all_nurses = constants["all_nurses"]
        num_weeks = constants["num_weeks"]
        h0_data = constants["h0_data"]
        week_number = constants["h0_data"]["week"]
        total_assignments_over_limit = soft_ILP_vars["total_assignments_over_limit"]
        total_unsatisfied_overtime = soft_ILP_vars["total_unsatisfied_overtime"]

        for n in all_nurses:
            if constants["configuration"]["h12"] and (
                n in constants["wd_data"]["vacations_with_ids"]
            ):
                continue

            if constants["configuration"]["s9"] and (nurses_data[n]["wantedOvertime"] == 0):
                continue

            worked_days_in_previous_weeks = h0_data["nurseHistory"][n][
                "numberOfAssignments"
            ]
            upper_limit = math.ceil(
                (
                    contracts_data[utils.contract_to_int[nurses_data[n]["contract"]]][
                        "maximumNumberOfAssignments"
                    ]
                    + nurses_data[n]["wantedOvertime"]
                )
                * ((week_number + 1) / num_weeks)
            )
            lower_limit = math.ceil(
                (
                    contracts_data[utils.contract_to_int[nurses_data[n]["contract"]]][
                        "maximumNumberOfAssignments"
                    ]
                    + nurses_data[n]["wantedOvertime"]
                )
                * ((week_number + 1) / num_weeks)
            )
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [total_assignments_over_limit[(n)], total_assignments[(n)]],
                        [-1, 1],
                    )
                ],
                senses=["L"],
                rhs=[upper_limit - worked_days_in_previous_weeks],
            )
            model.linear_constraints.add(
                lin_expr=[
                    cplex.SparsePair(
                        [total_unsatisfied_overtime[(n)], total_assignments[(n)]],
                        [1, 1],
                    )
                ],
                senses=["G"],
                rhs=[lower_limit - worked_days_in_previous_weeks],
            )


    def add_soft_constraints(self, model, basic_ILP_vars, soft_ILP_vars, constants):

        if constants["configuration"]["s1"]:
            self.add_shift_skill_req_optimal_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        if constants["configuration"]["s2"]:
            self.add_min_consecutive_shifts_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )
            self.add_max_consecutive_work_days_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )
            self.add_max_consecutive_work_shifts_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )
            self.add_min_consecutive_work_days_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        if constants["configuration"]["s3"]:
            self.add_max_consecutive_days_off_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )
            self.add_min_consecutive_days_off_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        if constants["configuration"]["s4"]:
            self.add_insatisfied_preferences_reqs_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        if constants["configuration"]["s6"]:
            self.add_total_assignments_out_of_bounds_constraint_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        if constants["configuration"]["s7"]:
            self.add_total_working_weekends_constraints_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        if constants["configuration"]["s8"]:
            self.add_total_assignments_with_if_needed_skill_constraints_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        if constants["configuration"]["s9"]:
            self.add_total_unsatisfied_overtime_constraints_soft(
                model, basic_ILP_vars, soft_ILP_vars, constants
            )

        # add_incomplete_weekends_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, constants)


    def save_tmp_results(self, results, solver, constants, basic_ILP_vars, soft_ILP_vars):
        num_days = constants["num_days"]
        num_nurses = constants["num_nurses"]
        num_skills = constants["num_skills"]
        num_shifts = constants["num_shifts"]
        week_number = constants["h0_data"]["week"]

        shifts_with_skills = basic_ILP_vars["shifts_with_skills"]

        if not solver.is_primal_feasible():
            return

        results[(week_number, "status")] = utils.STATUS_OK

        for n in range(num_nurses):
            for d in range(num_days):
                for s in range(num_shifts):
                    for sk in range(num_skills):
                        results[(n, d + 7 * week_number, s, sk)] = round(
                            solver.get_values(shifts_with_skills[n][d][s][sk])
                        )


    def set_objective_function(self, c, constants, basic_ILP_vars, soft_ILP_vars):
        all_nurses = constants["all_nurses"]
        all_shifts = constants["all_shifts"]
        all_skills = constants["all_skills"]
        all_days = constants["all_days"]

        sc_data = constants["sc_data"]

        num_nurses = constants["num_nurses"]
        num_shifts = constants["num_shifts"]
        num_skills = constants["num_skills"]
        num_days = constants["num_days"]

        insufficient_staffing = soft_ILP_vars["insufficient_staffing"]
        unsatisfied_preferences = soft_ILP_vars["unsatisfied_preferences"]
        total_working_weekends_over_limit = soft_ILP_vars[
            "total_working_weekends_over_limit"
        ]
        incomplete_weekends = basic_ILP_vars["incomplete_weekends"]
        total_assignments_over_limit = soft_ILP_vars["total_assignments_over_limit"]
        total_assignments_under_limit = soft_ILP_vars["total_assignments_under_limit"]
        violations_of_max_consecutive_working_days = soft_ILP_vars[
            "violations_of_max_consecutive_working_days"
        ]
        violations_of_max_consecutive_working_shifts = soft_ILP_vars[
            "violations_of_max_consecutive_working_shifts"
        ]
        violations_of_max_consecutive_days_off = soft_ILP_vars[
            "violations_of_max_consecutive_days_off"
        ]
        violations_of_min_consecutive_working_days = soft_ILP_vars[
            "violations_of_min_consecutive_working_days"
        ]
        violations_of_min_consecutive_days_off = soft_ILP_vars[
            "violations_of_min_consecutive_days_off"
        ]
        violations_of_min_consecutive_working_shifts = soft_ILP_vars[
            "violations_of_min_consecutive_working_shifts"
        ]
        total_assignments_with_if_needed_skill = soft_ILP_vars[
            "total_assignments_with_if_needed_skill"
        ]

        c.objective.set_sense(c.objective.sense.minimize)

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

        c.objective.set_linear(
            list(
                itertools.chain.from_iterable(
                    [
                        zip(
                            (
                                insufficient_staffing[(d, s, sk)]
                                for d in all_days
                                for s in all_shifts
                                for sk in all_skills
                            ),
                            [30] * num_days * num_shifts * num_skills,
                        ),
                        zip(
                            (
                                unsatisfied_preferences[(n, d, s)]
                                for n in all_nurses
                                for d in all_days
                                for s in all_shifts
                            ),
                            [10] * num_nurses * num_days * num_shifts,
                        ),
                        zip(
                            (total_working_weekends_over_limit[(n)] for n in all_nurses),
                            [30] * num_nurses,
                        ),
                        zip(
                            (incomplete_weekends[(n)] for n in all_nurses),
                            [30] * num_nurses,
                        ),
                        zip(
                            (total_assignments_over_limit[(n)] for n in all_nurses),
                            [20] * num_nurses,
                        ),
                        zip(
                            (total_assignments_under_limit[(n)] for n in all_nurses),
                            [20] * num_nurses,
                        ),
                        zip(
                            (
                                violations_of_max_consecutive_working_days[(n, d)]
                                for n in all_nurses
                                for d in all_days
                            ),
                            [30] * num_nurses * num_days,
                        ),
                        zip(
                            summed_violations_of_min_cons_working_days,
                            weights_of_violations_of_min_cons_working_days,
                        ),
                        zip(
                            summed_violations_of_min_cons_days_off,
                            weights_of_violations_of_min_cons_days_off,
                        ),
                        zip(
                            summed_violations_of_min_cons_shift_type,
                            weights_of_violations_of_min_cons_shift_type,
                        ),
                        zip(
                            (
                                violations_of_max_consecutive_days_off[(n, d)]
                                for n in all_nurses
                                for d in all_days
                            ),
                            [30] * num_nurses * num_days,
                        ),
                        zip(
                            (
                                violations_of_max_consecutive_working_shifts[(n, d, s)]
                                for n in all_nurses
                                for d in all_days
                                for s in all_shifts
                            ),
                            [15] * num_nurses * num_days * num_shifts,
                        ),
                        zip(
                            (
                                total_assignments_with_if_needed_skill[(n)]
                                for n in all_nurses
                            ),
                            [15] * num_nurses,
                        ),
                    ]
                )
            )
        )

        return


    def setup_problem(self, c, constants, results):
        self.prepare_help_constants(constants, results)

        # Create ILP variables.
        basic_ILP_vars = self.init_ilp_vars(c, constants)

        # Add hard constrains to model
        self.add_hard_constrains(c, basic_ILP_vars, constants)

        # soft_ILP_vars = {}
        soft_ILP_vars = self.init_ilp_vars_for_soft_constraints(c, basic_ILP_vars, constants)

        self.add_soft_constraints(c, basic_ILP_vars, soft_ILP_vars, constants)

        self.set_objective_function(c, constants, basic_ILP_vars, soft_ILP_vars)

        return basic_ILP_vars, soft_ILP_vars


    def compute_one_week(self, time_limit_for_week, constants, results):
        c = cplex.Cplex()
        c.parameters.mip.display.set(0)
        c.parameters.output.clonelog.set(0)
        # c.set_log_stream("log.txt")
        c.parameters.simplex.display.set(0)
        c.parameters.threads.set(1)
        c.parameters.timelimit.set(time_limit_for_week)
        c.parameters.mip.tolerances.absmipgap.set(0.0)
        c.parameters.emphasis.mip.set(c.parameters.emphasis.mip.values.optimality)

        basic_ILP_vars, soft_ILP_vars = self.setup_problem(c, constants, results)

        c.solve()
        sol = c.solution
        print(sol.get_method())
        print(f"number of threads: {c.parameters.threads.get()}")

        self.save_tmp_results(results, sol, constants, basic_ILP_vars, soft_ILP_vars)
