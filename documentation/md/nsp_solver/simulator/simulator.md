Module nsp_solver.simulator.simulator
=====================================

Classes
-------

`Simulator()`
:   Class responsible for the management of the whole process of computation of a schedule.

    ### Class variables

    `data: dict`
    :

    ### Methods

    `simulate_computation(self, input: nsp_solver.simulator.simulator.SimulatorInput)`
    :   Simulate the whole process of computation of a schedule.
        1. Loads the data from the input files.
        2. Evaluates the configuration.
        3. For each week it calls the solver for compuatation of the week and then calls the HistorySimulator to update the history.
        4. Calls the ScheduleValidator to evaluate the computed schedule.
        
        Args:
            input (SimulatorInput): object containg all inputs
        
        Returns:
            None: if the process is stopped by the user after the configuration evaluation
            (int, dict): the objective value of the computed schedule and the computed schedule as dictionary.

`SimulatorInput(config_file_path: str, history_file_path: str, scenario_file_path: str, week_files_paths: list, timelimit: int, solver: nsp_solver.solver.nsp_solver.NSP_solver, schedule_validator: nsp_solver.validator.validator.ScheduleValidator, config_validator: nsp_solver.validator.conf_validator.ConfigValidator, historySimulator: nsp_solver.simulator.history_simulator.HistorySimulator, graph_output_path: str, validator_output_path: str)`
:   Data class serving as an input for the Simulator class.
    It contains:
    the paths to the input files,
    the time limit for computation of 1 week,
    the chosen NSP_solver that will be used for the computation,
    the ScheduleValidator, ConfigValidator, HistorySimulator that will be used during the process of the schedule computation,
    the paths to the output files.

    ### Class variables

    `config_file_path: str`
    :

    `config_validator: nsp_solver.validator.conf_validator.ConfigValidator`
    :

    `graph_output_path: str`
    :

    `historySimulator: nsp_solver.simulator.history_simulator.HistorySimulator`
    :

    `history_file_path: str`
    :

    `scenario_file_path: str`
    :

    `schedule_validator: nsp_solver.validator.validator.ScheduleValidator`
    :

    `solver: nsp_solver.solver.nsp_solver.NSP_solver`
    :

    `timelimit: int`
    :

    `validator_output_path: str`
    :

    `week_files_paths: list`
    :