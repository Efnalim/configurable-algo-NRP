Module nsp_solver.solver.nsp_solver
===================================

Classes
-------

`NSP_solver()`
:   Abstract class that serves as the interface for solvers used for a compuation of a schedule for a week.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * nsp_solver.solver.nsp_cplex.CplexSolver
    * nsp_solver.solver.nsp_docplex.DOCPLEX_Solver
    * nsp_solver.solver.nsp_or_tools.ORTOOLS_Solver

    ### Class variables

    `name: str`
    :

    ### Methods

    `compute_one_week(self, time_limit_for_week, data, results)`
    :   Computes a schedule for a week given a time limit and data.
        
        Args:
            time_limit_for_week (int): time limit for finding a schedule as optimal as possible
            data (dict): dictionary that contains data from input files
            results (dict): dictionary used to store partially computed schedule