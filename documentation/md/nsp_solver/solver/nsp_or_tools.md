Module nsp_solver.solver.nsp_or_tools
=====================================

Classes
-------

`ORTOOLS_Solver()`
:   Child Class from NSP_solver that uses CP SAT solver from OR-TOOLS to compute a schedule per week.

    ### Ancestors (in MRO)

    * nsp_solver.solver.nsp_solver.NSP_solver
    * abc.ABC

    ### Class variables

    `name: str`
    :

    ### Methods

    `add_hard_constrains(self, model, basic_CP_vars, data)`
    :   Adds all hard constraints to the model.

    `add_insatisfied_preferences_reqs(self, model, preferences, unsatisfied_preferences, shifts, all_nurses, all_days, all_shifts, all_skills)`
    :   Adds the soft constraint that introduces the preferences of nurses for specific assignments/non-assignments.

    `add_min_consecutive_days_off_constraint(self, model, basic_CP_vars, soft_CP_vars, data)`
    :   Adds the soft constraint that penilizes a number of consecutive days off under the minimum specified in the contract of each nurse.
        
        Args:
            model: object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_shifts_constraint(self, model, basic_CP_vars, soft_CP_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive shifts of one type under the minimum specified in the scenario.
        
        Args:
            model: object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_working_days_constraint(self, model, basic_CP_vars, soft_CP_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive working days under the minimum specified in the constract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_missing_skill_req(self, model, nurses_data, shifts_with_skills, all_days, all_shifts, all_skills)`
    :   Adds hard constraint that disables nurses working shift with a skill that they do not possess.

    `add_shift_skill_req(self, model, req, basic_CP_vars, soft_CP_vars, data)`
    :   Adds hard constraint that dictates minimal number of nurses in a shift working with specific skill.

    `add_shift_succession_reqs(self, model, shifts, all_nurses, all_days, all_shifts, num_days, data)`
    :   Adds hard constraint that disables invalid pairs of succcessive shift types.

    `add_soft_constraints(self, model, basic_CP_vars, soft_CP_vars, data)`
    :   Adds the soft constraints to the model.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week

    `add_total_incomplete_weekends_constraint(self, model, nurses_data, contracts_data, total_incomplete_weekends, working_weekends, shifts, working_days, all_nurses, all_days, all_shifts)`
    :   Adds the soft constraint that penilizes incomplete weekends.

    `add_total_working_days_out_of_bounds_constraint(self, model, nurses_data, contracts_data, history, total_working_days, total_working_days_over_limit, total_working_days_under_limit, all_nurses)`
    :   Adds the soft constraint that penilizes more working weekends than the specified maximum.

    `add_total_working_weekends_soft_constraints(self, model, nurses_data, contracts_data, history, total_working_weekends_over_limit, working_weekends, all_nurses)`
    :   Adds the soft constraint that penilizes more working weekends than the specified maximum.

    `init_cp_vars(self, model, data)`
    :   Initializes basic variables for primarly for hard contraints.
        Returns a dictionary 'basic_cp_vars' containing the names of those variables for further manipulation.

    `init_cp_vars_for_soft_constraints(self, model, basic_CP_vars, data)`
    :   Adds variables used by the soft constraints.
        
        Args:
            model: object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        
        Returns:
            dict: the variables added to the mathematical model

    `save_tmp_results(self, results, solver, status, data, basic_CP_vars, soft_CP_vars, week_number)`
    :   Stores the solution into the results dictionary.
        
        Args:
            results (dict): dictionary used to store partially computed schedule
            solver : object that contains the computed solution
            status : status of the solution
            data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            week_number (int): number of the computed week

    `set_objective_function(self, model, basic_CP_vars, soft_CP_vars, data)`
    :   Sets the objective function contatining all penalties from all enabled constraints.