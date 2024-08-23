import copy
from dataclasses import dataclass
import json
from matplotlib import pyplot as plt, ticker
from nsp_solver.simulator.history_simulator import HistorySimulator
from nsp_solver.solver.nsp_solver import NSP_solver
from nsp_solver.utils import utils
from nsp_solver.validator.conf_validator import CONF_EVAL, ConfigValidator
from nsp_solver.validator.validator import ScheduleValidator
import numpy as np


@dataclass
class SimulatorInput():
    config_file_path: str
    history_file_path: str
    scenario_file_path: str
    week_files_paths: list[str]
    timelimit: int
    solver: NSP_solver
    schedule_validator: ScheduleValidator
    config_validator: ConfigValidator
    historySimulator: HistorySimulator
    graph_output_path: str
    validator_output_path: str


class Simulator:
    data: dict = {}

    def simulate_computation(self, input: SimulatorInput):
        self._load_data(input)

        if input.config_validator.evaluate_configuration(self.data) is CONF_EVAL.STOP:
            return

        time_limit_for_week = input.timelimit
        if time_limit_for_week == 0:
            time_limit_for_week = 10 + 10 * (self.data["num_nurses"] - 20)

        results = self._get_empty_results()

        fail = False
        # accumulate results over weeks
        for week_number in range(self.data["number_weeks"]):
            self.data["wd_data"] = self.data["all_wd_data"][week_number]
            input.solver.compute_one_week(time_limit_for_week, self.data, results)
            if results[(week_number, "status")] == utils.STATUS_FAIL:
                fail = True
                break
            input.historySimulator.update_history_for_next_week(results, self.data, week_number)

        if fail:
            total_value = 99999
        else:
            validator = ScheduleValidator()
            # total_value = validator.evaluate_schedule(results, self.data, 'outputs/validator_result.txt')
            total_value = validator.evaluate_schedule(results, self.data, input.validator_output_path)

        if input.graph_output_path is not None:
            self._display_schedule(results, input.graph_output_path)

        return total_value, results

    def _load_data(self, input: SimulatorInput):
        with open(input.config_file_path) as config_file:
            config_data = json.load(config_file)

        with open(input.history_file_path) as history_file:
            history_data = json.load(history_file)

        with open(input.scenario_file_path) as scenario_file:
            sc_data = json.load(scenario_file)

        wd_data = []
        for week_file_path in input.week_files_paths:
            with open(week_file_path) as week_file:
                wd_data.append(json.load(week_file))

        # initialize self.data
        number_weeks = len(input.week_files_paths)
        num_nurses = len(sc_data["nurses"])
        num_shifts = len(sc_data["shiftTypes"])
        num_skills = len(sc_data["skills"])
        num_days = 7
        all_nurses = range(num_nurses)
        all_shifts = range(num_shifts)
        all_days = range(num_days)
        all_skills = range(num_skills)
        all_weeks = range(number_weeks)

        self.data["configuration"] = config_data
        self.data["h0_data"] = history_data
        self.data["h0_data_original"] = copy.deepcopy(history_data)
        self.data["sc_data"] = sc_data
        self.data["wd_data"] = wd_data[0]
        self.data["all_wd_data"] = wd_data
        self.data["number_weeks"] = number_weeks
        self.data["num_nurses"] = num_nurses
        self.data["num_shifts"] = num_shifts
        self.data["num_skills"] = num_skills
        self.data["num_days"] = num_days
        self.data["num_weeks"] = number_weeks
        self.data["all_nurses"] = all_nurses
        self.data["all_shifts"] = all_shifts
        self.data["all_days"] = all_days
        self.data["all_skills"] = all_skills
        self.data["all_weeks"] = all_weeks

    def _get_empty_results(self) -> dict:
        results = {}
        for w in self.data["all_weeks"]:
            for n in self.data["all_nurses"]:
                for d in self.data["all_days"]:
                    for s in self.data["all_shifts"]:
                        for sk in self.data["all_skills"]:
                            results[(n, d + 7 * w, s, sk)] = 0
        return results

    def _display_schedule(self, results, filename):
        """
        Displays computed schedule as table in a figure.
        """

        num_days = self.data["num_days"] * self.data["number_weeks"]
        num_nurses = self.data["num_nurses"]
        num_skills = self.data["num_skills"]
        num_shifts = self.data["num_shifts"]
        num_days_in_week = self.data["num_days"]

        schedule_table = np.zeros([num_nurses, num_days * num_shifts])
        legend = np.zeros([1, num_skills + 2])

        for d in range(num_days):
            for n in range(num_nurses):
                for s in range(num_shifts):
                    for sk in range(num_skills):
                        if results[(n, d, s, sk)] == 1:
                            schedule_table[n][d * num_shifts + s] = 0.85 - (0.175 * sk)

        if self.data["configuration"]["h12"]:
            for w in self.data["all_weeks"]:
                for n in self.data["all_wd_data"][w]["vacations"]:
                    nurse_id = int(n.split("_")[1])
                    for d in range(num_days_in_week):
                        for s in range(num_shifts):
                            schedule_table[nurse_id][(d + 7 * w)*num_shifts + s] = 1

        for sk in range(num_skills):
            legend[0][sk] = 0.85 - (0.175 * sk)
        legend[0][num_skills + 1] = 1

        fig, (ax0, ax1) = plt.subplots(
            2, 1, figsize=(16, 9), gridspec_kw={"height_ratios": [10, 1]}
        )

        ax0.pcolor(schedule_table)
        ax0.set_title("Schedule")
        ax0.set_xticks(np.arange(num_days * num_shifts))
        ax0.set_xticklabels(np.arange(num_days * num_shifts) / 4)
        ax0.tick_params(axis="x", bottom=True, top=True, labelbottom=True, labeltop=True)

        ax0.xaxis.set_major_locator(ticker.MultipleLocator(4))

        ax1.pcolor(legend, edgecolors="k", linewidths=5)
        ax1.set_title("Legend - skills")
        ax1.set_xticks(np.arange(num_skills + 2) + 0.5)
        ax1.set_xticklabels(
            ["HeadNurse", "Nurse", "Caretaker", "Trainee", "Not working", "Vacation"]
        )

        fig.tight_layout()
        plt.savefig(filename)
