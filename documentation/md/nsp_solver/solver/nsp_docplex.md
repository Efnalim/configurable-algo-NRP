Module nsp_solver.solver.nsp_docplex
====================================

Classes
-------

`DOCPLEX_Solver()`
:   Child Class from NSP_solver that uses CP solver from docplex API to compute a schedule per week.

    ### Ancestors (in MRO)

    * nsp_solver.solver.nsp_solver.NSP_solver
    * abc.ABC

    ### Class variables

    `name: str`
    :

    ### Methods

    `add_hard_constrains(self, model, basic_cp_vars, data)`
    :   Adds all hard constraints to the model.

    `add_incomplete_weekends_constraint(self, model, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that penilizes incomplete weekends.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_insatisfied_preferences_reqs(self, model, wd_data, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that introduces the preferences of nurses for specific assignments/non-assignments.
        
        Args:
            model : object that represents the mathematical model
            wd_data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_days_off_constraint(self, model, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that bans assignment of any number of consecutive days off over the maximum specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_work_days_constraint(self, model, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive working days over the maximum specified in the constract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_work_shifts_constraint(self, model, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that penilizes assignment of any number of consecutive shifts of one type over the maximum specified in the scenario.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_days_off_constraint(self, model, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that penilizes a number of consecutive days off under the minimum specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_shifts_constraint(self, model, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive shifts of one type under the minimum specified in the scenario.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_work_days_constraint(self, model, basic_cp_vars, soft_cp_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive working days under the minimum specified in the constract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_missing_skill_req(self, model, nurses_data, shifts_with_skills, all_days, all_shifts, all_skills)`
    :   Adds hard constraint that disables nurses working shift with a skill that they do not possess.

    `add_shift_skill_req_minimal(self, model, req, basic_cp_vars, data)`
    :   Adds hard constraint that dictates minimal number of nurses in a shift working with specific skill.

    `add_shift_skill_req_optimal(self, model, req, basic_cp_vars, soft_cp_vars, data)`
    :   Add
        
        Args:
            model : object that represents the mathematical model
            req (dict): requirements for the coverage
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_shift_succession_reqs(self, model, shifts, all_nurses, all_days, all_shifts, num_days, data, basic_cp_vars)`
    :   Adds hard constraint that disables invalid pairs of succcessive shift types.

    `add_soft_constraints(self, model, basic_cp_vars, soft_cp_vars, data, week_number)`
    :   Adds the soft constraints to the model.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week

    `add_total_working_days_out_of_bounds_constraint(self, model, basic_cp_vars, soft_cp_vars, data, week_number)`
    :   Adds the soft constraint that penilizes total assignments out of bounds specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week

    `add_total_working_weekends_soft_constraints(self, model, basic_cp_vars, soft_cp_vars, data, week_number)`
    :   Adds the soft constraint that penilizes more working weekends than the specified maximum.
        
        Args:
            model : object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week

    `init_cp_vars(self, model, data)`
    :   Initializes basic variables for primarly for hard contraints.
        Returns a dictionary 'basic_cp_vars' containing the names of those variables for further manipulation.

    `init_cp_vars_for_soft_constraints(self, model, basic_cp_vars, data)`
    :   Adds variables used by the soft constraints.
        
        Args:
            model: object that represents the mathematical model
            basic_cp_vars (dict): contains the variables of the mathematical model
            data (dict): dictionary that contains data from input files
        
        Returns:
            dict: the variables added to the mathematical model

    `save_tmp_results(self, results, sol, data, basic_cp_vars, soft_cp_vars, week_number, model)`
    :   Stores the solution into the results dictionary.
        
        Args:
            results (dict): dictionary used to store partially computed schedule
            sol : object that contains the computed solution
            data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model
            week_number (int): number of the computed week
            model : object that represents the mathematical model

    `set_objective_function(self, model, data, basic_cp_vars, soft_cp_vars)`
    :   Sets the objective function contatining all penalties from all enabled constraints.
        
        Args:
            model : object that represents the mathematical model
            data (dict): dictionary that contains data from input files
            basic_cp_vars (dict): contains the variables of the mathematical model
            soft_cp_vars (dict): contains the variables of the mathematical model

    `setup_problem(self, c, data, week_number)`
    :   Sets up the mathematical model to be solved.
        
        Args:
            model: object that represents the mathematical model
            data (dict): dictionary that contains data from input files
            week_number (int): number of the computed week
        
        Returns:
            (dict, dict): 2 dictionaries that contains names of variables of the mathematical model