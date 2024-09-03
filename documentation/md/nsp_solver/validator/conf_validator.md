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
:   _summary_

    ### Methods

    `evaluate_configuration(self, data) ‑> nsp_solver.validator.conf_validator.CONF_EVAL`
    :   _summary_
        
        Args:
            data (dict): dictionary that contains data from input files
        
        Returns:
            CONF_EVAL: _description_