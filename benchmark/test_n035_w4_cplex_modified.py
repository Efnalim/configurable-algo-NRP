#!/usr/bin/python

import os
import sys
import subprocess

from contextlib import contextmanager

original_stdout = sys.stdout

@contextmanager
def redirect_stdout_to_file(file_path):
    original_stdout = sys.stdout
    with open(file_path, 'w') as file:
        sys.stdout = file
        yield
    sys.stdout = original_stdout


try:
    output_file = 'outputs\\logs\\output_test_n035_w4_cplex_modified.txt'

    if not os.path.exists("outputs"): 
        os.makedirs("outputs") 
    if not os.path.exists("outputs\\logs"): 
        os.makedirs("outputs\\logs") 
    if not os.path.exists("outputs\\schedules"): 
        os.makedirs("outputs\\schedules") 

    number_of_iteration = 1
    number_of_nurses = 35
    time_limit = 0
    solver_id = 0
    modified = 1

    week_combinations = []
    with open('input\\week_combinations.txt') as f:
        week_combinations = [line.strip() for line in f.readlines()]

    # list of input for benchmark
    with redirect_stdout_to_file(output_file):
        arguments_list = [ f'{modified} {time_limit} {solver_id} {number_of_nurses} ' + combination for combination in week_combinations]

        # run the main script in iterations
        for arg in arguments_list:
            for _ in range(number_of_iteration):
                subprocess.run(['python', 'main.py'] + arg.split(' '), stdout=sys.stdout)

    # filter unwanted lines from the output file
    # with open(output_file, 'r') as file:
    #     lines = file.readlines()

    # filtered_lines = [line for line in lines if "PARAM" not in line]
    # filtered_lines = [line for line in filtered_lines if "Version" not in line]

    # with open(output_file, 'w') as file:
    #     file.writelines(filtered_lines)

except Exception as e:
    sys.stdout = original_stdout
    print(f"An error occurred: {e}")
