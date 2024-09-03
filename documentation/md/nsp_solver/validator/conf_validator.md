Module nsp_solver.validator.conf_validator
==========================================

Classes
-------

`CONF_EVAL(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CONTINUE_EVEN_THOUGH`
    :

    `OK`
    :

    `STOP`
    :

`ConfigValidator()`
:   Class responsible for validating the configuration of a nurse rostering problem.

    ### Methods

    `evaluate_configuration(self, data) ‑> nsp_solver.validator.conf_validator.CONF_EVAL`
    :   Evaluates the configuration and asks the user if there is a conflict between enabled constraints.
        
        Args:
            data (dict): dictionary that contains data from input files
        
        Returns:
            CONF_EVAL: evaluation result that decides whether the computation will be performed or stopped