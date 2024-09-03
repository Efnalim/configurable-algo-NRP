Module nsp_solver.solver.nsp_docplex_all_diff_min_soft
======================================================

Functions
---------

    
`add_hard_constrains(model, basic_cp_vars, data)`
:   Adds all hard constraints to the model.

    
`add_incomplete_weekends_constraint(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_insatisfied_preferences_reqs(model, wd_data, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_max_consecutive_days_off_constraint(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_max_consecutive_work_days_constraint(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_max_consecutive_work_shifts_constraint(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_min_consecutive_days_off_constraint(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_min_consecutive_shifts_constraint(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_min_consecutive_work_days_constraint(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_missing_skill_req(model, nurses_data, shifts_with_skills, all_days, all_shifts, all_skills, basic_cp_vars)`
:   Adds hard constraint that disables nurses working shift with a skill that they do not possess.

    
`add_shift_skill_req_minimal(model, req, basic_cp_vars, data)`
:   Adds hard constraint that dictates minimal number of nurses in a shift working with specific skill.

    
`add_shift_skill_req_optimal(model, basic_cp_vars, soft_cp_vars, data)`
:   

    
`add_shift_succession_reqs(model, shifts, all_nurses, all_days, all_shifts, num_days, data, basic_cp_vars)`
:   Adds hard constraint that disables invalid pairs of succcessive shift types.

    
`add_soft_constraints(model, basic_cp_vars, soft_cp_vars, data, week_number)`
:   

    
`add_total_working_days_out_of_bounds_constraint(model, basic_cp_vars, soft_cp_vars, data, week_number)`
:   

    
`add_total_working_weekends_soft_constraints(model, basic_cp_vars, soft_cp_vars, data, week_number)`
:   

    
`compute_one_week(time_limit_for_week, week_number, data, results)`
:   

    
`init_cp_vars(model, data)`
:   Initializes basic variables for primarly for hard contraints.
    Returns a dictionary 'basic_cp_vars' containing the names of those variables for further manipulation.

    
`init_cp_vars_for_soft_constraints(model, basic_cp_vars, data)`
:   

    
`save_tmp_results(results, solver, data, basic_cp_vars, soft_cp_vars, week_number, model)`
:   

    
`set_objective_function(model, data, basic_cp_vars, soft_cp_vars)`
:   

    
`setup_problem(c, data, week_number)`
: