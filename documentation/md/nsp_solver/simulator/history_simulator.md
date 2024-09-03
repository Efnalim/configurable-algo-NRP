Module nsp_solver.simulator.history_simulator
=============================================

Classes
-------

`HistorySimulator()`
:   Class responsible for updating the history data for computation of the next week.

    ### Methods

    `update_history_for_next_week(self, results: dict, data: dict)`
    :   Updates the value of data["h0_data"] with new data derived from the newly computed week.
        
        Args:
            results (dict): partially computed schedule
            data (dict): data from input files