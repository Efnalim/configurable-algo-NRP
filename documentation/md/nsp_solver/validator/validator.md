Module nsp_solver.validator.validator
=====================================

Classes
-------

`ScheduleValidator()`
:   Class responsible for validating the computed schedule

    ### Methods

    `evaluate_schedule(self, schedule, data, output_file_path=None) ‑> int`
    :   Evaluates the computed schedule. 
        
        Args:
            schedule (dict): computed schedule
            data (dict): dictionary that contains data from input files
            output_file_path (str, optional): Path for the written output of the evaluation. Defaults to None.
        
        Returns:
            int: value of the evaluated schedule (99999 if invalid)