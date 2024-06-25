#!/usr/bin/python

import random
import sys
import os 

if __name__ == "__main__":

    if not os.path.exists("..\\input"): 
        os.makedirs("..\\input") 

    num_weeks = int(sys.argv[1])
    num_combinations = int(sys.argv[2])
    filename = "..\\input\\week_combinations.txt"
    with open(filename, "w") as f:
        for _ in range(num_combinations):
            combination = f"{num_weeks} {random.randint(0, 2)}"
            for _ in range(num_weeks):
                combination = combination + f" {random.randint(0, 9)}"
            f.write(combination + '\n')
