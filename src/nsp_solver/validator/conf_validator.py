from enum import Enum
from tkinter import LEFT, RIGHT, IntVar, Label, Tk, ttk


class CONF_EVAL(Enum):
    OK = 0
    CONTINUE_EVEN_THOUGH = 1
    STOP = 2


class ConfigValidator:
    def __init__(self):
        pass

    def evaluate_configuration(self, constants) -> CONF_EVAL:
        retval = CONF_EVAL.OK

        retval = self.__update_conf_eval_retval(
            retval, self._check_overriding(constants)
        )
        retval = self.__update_conf_eval_retval(
            retval, self._check_contradicting(constants)
        )
        retval = self.__update_conf_eval_retval(
            retval, self._check_affecting(constants)
        )

        return retval

    def _check_overriding(self, constants) -> CONF_EVAL:
        conf = constants["configuration"]
        if conf["h1"] and conf["h10"]:
            return self._get_user_choice(
                "Hard constraint H1 overrides hard constraint H10. \nDo you want to continue?"
            )
        return CONF_EVAL.OK

    def _check_contradicting(self, constants) -> CONF_EVAL:
        conf = constants["configuration"]
        if not conf["h6"] or not conf["h9"]:
            return CONF_EVAL.OK
        for contract in constants["sc_data"]["contracts"]:
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

    def _check_affecting(self, constants) -> CONF_EVAL:
        conf = constants["configuration"]
        if not conf["h5"] or not conf["s2"]:
            return CONF_EVAL.OK
        for contract in constants["sc_data"]["contracts"]:
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
        return new_retval if new_retval.value > retval.value else retval

    def __get_dialog_popup(self, question) -> CONF_EVAL:
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
        win, _, _, _, selected_option = (
            self.__get_dialog_popup(question)
        )
        win.mainloop()
        win.destroy()
        return CONF_EVAL(selected_option.get())