from enum import Enum
from tkinter import LEFT, RIGHT, IntVar, Label, Tk, ttk


class CONF_EVAL(Enum):
    OK = 0
    CONTINUE_EVEN_THOUGH = 1
    STOP = 2


class ConfigValidator:
    """Class responsible for validating the configuration of a nurse rostering problem.
    """

    def evaluate_configuration(self, data) -> CONF_EVAL:
        """Evaluates the configuration and asks the user if there is a conflict between enabled constraints.

        Args:
            data (dict): dictionary that contains data from input files

        Returns:
            CONF_EVAL: evaluation result that decides whether the computation will be performed or stopped
        """
        retval = CONF_EVAL.OK

        retval = self.__update_conf_eval_retval(
            retval, self._check_overriding(data)
        )
        retval = self.__update_conf_eval_retval(
            retval, self._check_contradicting(data)
        )
        retval = self.__update_conf_eval_retval(
            retval, self._check_affecting(data)
        )

        return retval

    def _check_overriding(self, data) -> CONF_EVAL:
        """Checks configuration of possibly overriding constraints.

        Args:
            data (dict): dictionary that contains data from input files

        Returns:
            CONF_EVAL: evaluation result that decides whether the computation will be performed or stopped
        """
        conf = data["configuration"]
        if conf["h1"] and conf["h10"]:
            return self._get_user_choice(
                "Hard constraint H1 overrides hard constraint H10. \nDo you want to continue?"
            )
        return CONF_EVAL.OK

    def _check_contradicting(self, data) -> CONF_EVAL:
        """Checks configuration of possibly contradicting constraints.

        Args:
            data (dict): dictionary that contains data from input files

        Returns:
            CONF_EVAL: evaluation result that decides whether the computation will be performed or stopped
        """
        conf = data["configuration"]
        if not conf["h6"] or not conf["h9"]:
            return CONF_EVAL.OK
        for contract in data["sc_data"]["contracts"]:
            if (
                contract["minimalFreePeriod"]
                > contract["maximumNumberOfConsecutiveDaysOffHard"]
            ):
                return self._get_user_choice(
                    "Hard constraints H6 and H9 are contradicting each other.\
                    \nMinimal free period has more days than the hard maximum number of consecutive days off. \
                    \nNo solution will be found. \nDo you want to continue?"
                )
        return CONF_EVAL.OK

    def _check_affecting(self, data) -> CONF_EVAL:
        """Checks configuration of constraints that possibly affect each other.

        Args:
            data (dict): dictionary that contains data from input files

        Returns:
            CONF_EVAL: evaluation result that decides whether the computation will be performed or stopped
        """
        conf = data["configuration"]
        if not conf["h5"] or not conf["s2"]:
            return CONF_EVAL.OK
        for contract in data["sc_data"]["contracts"]:
            if (
                contract["maximumNumberOfConsecutiveWorkingDaysHard"]
                < contract["minimumNumberOfConsecutiveWorkingDays"]
            ):
                return self._get_user_choice(
                    "Hard constraints H5 affects soft constraints S2. \
                    \nThe hard maximum number of consecutive working days is smaller than \
                    the soft minimum number of consecutive working days. \
                    \nThe objective value of found solution will be negatively affected. \
                    \nDo you want to continue?"
                )
        return CONF_EVAL.OK

    def __update_conf_eval_retval(self, retval: CONF_EVAL, new_retval: CONF_EVAL):
        """Updated the value to the higher value of CONF_EVAL

        Args:
            retval (CONF_EVAL): _description_
            new_retval (CONF_EVAL): _description_

        Returns:
            CONF_EVAL: the higher level of CONF_EVAL
        """
        return new_retval if new_retval.value > retval.value else retval

    def __get_dialog_popup(self, question) -> CONF_EVAL:
        """Returns the popup window and its elements for the given question

        Args:
            question (str): question that is displayed in the popup window
        """
        def stop_option():
            selected_option.set(CONF_EVAL.STOP.value)
            win.quit()

        def continue_option():
            selected_option.set(CONF_EVAL.CONTINUE_EVEN_THOUGH.value)
            win.quit()

        win = Tk()
        win.title("Warning")
        win.config(width=200, height=150)
        style = ttk.Style()
        style.theme_use("clam")

        selected_option = IntVar()

        label = Label(win, text=question)
        label.pack(pady=20)

        button_stop = ttk.Button(win, text="Stop", command=stop_option)
        button_stop.pack(side=LEFT, padx=20, pady=20)
        button_continue = ttk.Button(win, text="Continue", command=continue_option)
        button_continue.pack(side=RIGHT, padx=20, pady=20)

        return win, label, button_stop, button_continue, selected_option

    def _get_user_choice(self, question):
        """Opens the popup window and wait for the user to make a choice.

        Args:
            question (str): question that is displayed in the popup window

        Returns:
            CONF_EVAL: decidion of the user
        """
        win, _, _, _, selected_option = (
            self.__get_dialog_popup(question)
        )
        win.mainloop()
        win.destroy()
        return CONF_EVAL(selected_option.get())
