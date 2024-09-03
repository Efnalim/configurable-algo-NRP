Module nsp_solver.solver.nsp_cplex
==================================

Classes
-------

`CplexSolver()`
:   Child Class from NSP_solver that uses MILP cplex solver via API to compute a schedule per week.

    ### Ancestors (in MRO)

    * nsp_solver.solver.nsp_solver.NSP_solver
    * abc.ABC

    ### Class variables

    `name: str`
    :

    ### Methods

    `add_hard_constrains(self, model, basic_ILP_vars, data)`
    :   Adds all hard constraints to the model.
        
        Args:
            model (_type_): _description_
            basic_ILP_vars (_type_): _description_
            data (_type_): _description_

    `add_incomplete_weekends_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes incomplete weekends.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_insatisfied_preferences_reqs_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that introduces the preferences of nurses for specific assignments/non-assignments.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_days_off_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that bans assignment of any number of consecutive days off over the maximum specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_days_off_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that bans assignment of any number of consecutive days off over the maximum specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_work_days_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that bans assignment of any number of consecutive working days over the maximum specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_work_days_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive working days over the maximum specified in the constract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_work_shifts_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that bans assignment of any number of consecutive shifts of one type over the maximum specified in the scenario.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_consecutive_work_shifts_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes assignment of any number of consecutive shifts of one type over the maximum specified in the scenario.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_incomplete_weekends_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the soft constraint that penilizes incomplete weekends.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_min_total_assignments_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that enforces that total number of assignemnts a nurse are in the limits specified in the contract of the nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_one_shift_per_day_constraint(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that bans multiple assignments of a nurse on one day.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_one_shift_per_day_exception_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that bans multiple assignments of a nurse on one day with the exception of early and night shifts on the same day.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_max_shift_of_given_type_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that disallows more assignments to a specific shift type than it is allowed.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_days_off_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the soft constraint that bans any number of consecutive days off under the minimum specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_days_off_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes a number of consecutive days off under the minimum specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_shifts_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that bans assignment of a number of consecutive shifts of one type under the minimum specified in the scenario.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_shifts_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive shifts of one type under the minimum specified in the scenario.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_work_days_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive working days under the minimum specified in the constract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_consecutive_work_days_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes assignment of a number of consecutive working days under the minimum specified in the constract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_min_continuous_free_period_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that enforces that every nurse has a minimal continuous period of days off.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_missing_skill_req(self, model, basic_ILP_vars, data)`
    :   Adds hard constraint that disables nurses working shift with a skill that they do not possess.
        
        Args:
            model (_type_): _description_
            basic_ILP_vars (_type_): _description_
            data (_type_): _description_

    `add_shift_skill_req_minimal(self, model, basic_ILP_vars, data)`
    :   Adds hard constraint that dictates minimal number of nurses in a shift working with specific skill.
        
        Args:
            model (_type_): _description_
            basic_ILP_vars (_type_): _description_
            data (_type_): _description_

    `add_shift_skill_req_optimal_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that introduces the optimal number of assigned nurses for each combination of day, shift, skill.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_shift_succession_reqs(self, model, basic_ILP_vars, data)`
    :   Adds hard constraint that disables invalid pairs of succcessive shift types.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_soft_constraints(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraints to the model.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_total_assignments_out_of_bounds_constraint_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes total assignments out of bounds specified in the contract of each nurse.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_total_assignments_with_if_needed_skill_constraints_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes any assigment of nurse using a skill that is labeled as "if needed".
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_total_unsatisfied_overtime_constraints_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes unsatisfied wanted overtime per assignment.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_total_working_weekends_constraints_soft(self, model, basic_ILP_vars, soft_ILP_vars, data)`
    :   Adds the soft constraint that penilizes more working weekends than the specified maximum.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `add_vacations_reqs_constraint_hard(self, model, basic_ILP_vars, data)`
    :   Adds the hard constraint that bans assignments fot a nurse that is has planned a vacation.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files

    `init_ilp_vars(self, model, data)`
    :   Initializes basic variables for primarly for hard contraints.
        
        Args:
            model: object that represents the mathematical model
            data (dict): dictionary that contains data from input files
        
        Returns:
            dict: dictionary 'basic_ILP_vars' that contains the names variables of the mathematical model

    `init_ilp_vars_for_soft_constraints(self, model, basic_ILP_vars, data)`
    :   Adds the variables used for soft constraints to the model.
        
        Args:
            model : object that represents the mathematical model
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            data (dict): dictionary that contains data from input files
        
        Returns:
            dic: dictionary that contains the names of introduced variables

    `prepare_help_data(self, data, results)`
    :   Prepares helpful data for other methods.
        
        Args:
            data (dict): dictionary that contains data from input files
            results (dict): dictionary used to store partially computed schedule

    `save_tmp_results(self, results, sol, data, basic_ILP_vars, soft_ILP_vars)`
    :   Stores the solution into the results dictionary.
        
        Args:
            results (dict): dictionary used to store partially computed schedule
            sol (_type_): _description_
            data (dict): dictionary that contains data from input files
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model

    `set_objective_function(self, model, data, basic_ILP_vars, soft_ILP_vars)`
    :   Sets the objective function contatining all penalties from all enabled constraints.
        
        Args:
            model : object that represents the mathematical model
            data (dict): dictionary that contains data from input files
            basic_ILP_vars (dict): contains the names variables of the mathematical model
            soft_ILP_vars (dict): contains the names variables of the mathematical model

    `setup_problem(self, model, data, results)`
    :   Sets up the mathematical model to be solved.
        
        Args:
            model : object that represents the mathematical model
            data (dict): dictionary that contains data from input files
            results (dict): dictionary used to store partially computed schedule
        
        Returns:
            (dict, dict): 2 dictionaries that contains names of variables of the mathematical model