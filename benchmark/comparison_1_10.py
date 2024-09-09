#!/usr/bin/python

import os
import sys
import subprocess

from nsp_solver.utils import utils

original_stdout = sys.stdout

try:
    output_file = 'outputs\\logs\\output_comparison_1_10.txt'

    if not os.path.exists("outputs"): 
        os.makedirs("outputs") 
    if not os.path.exists("outputs\\logs"): 
        os.makedirs("outputs\\logs") 
    if not os.path.exists("outputs\\schedules"): 
        os.makedirs("outputs\\schedules") 

    number_of_iteration = 10
    number_of_nurses = 35
    config_file_id = 0

    week_combinations = []
    with open('input\\week_combinations.txt') as f:
        week_combinations = [line.strip() for line in f.readlines()]


    with open('outputs/results.txt', 'w') as file:
        ajustment = 7 + len(week_combinations[0])
        file.write("solver  | " + "configuration".ljust(ajustment) + " | value | time\n")
        file.write("-----------------------------------------------------------\n")

    # list of input for benchmark
    with utils.redirect_stdout_to_file(output_file):
        # print(arguments_list)
        # run the main script in iterations
        for time_limit in [0]:
            for solver_id in [1, 2]:
                arguments_list = [ f'{time_limit} {solver_id} {number_of_nurses} {config_file_id} ' + combination for combination in week_combinations]
                for arg in arguments_list:
                    for _ in range(number_of_iteration):
                        subprocess.run(['python', 'mainbasic.py'] + arg.split(' '), stdout=sys.stdout)

except Exception as e:
    sys.stdout = original_stdout
    print(f"An error occurred: {e}")

