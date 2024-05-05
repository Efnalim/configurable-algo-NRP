#!/usr/bin/python

import random
import sys
import os 

if __name__ == "__main__":

    if not os.path.exists("..\\input"): 
        os.makedirs("..\\input") 

    num_combinations = int(sys.argv[1])
    filename = "..\\input\\week_combinations.txt"
    with open(filename, "w") as f:
        for _ in range(num_combinations):
            f.write(f"4 {random.randint(0, 2)} {random.randint(0, 9)} {random.randint(0, 9)} {random.randint(0, 9)} {random.randint(0, 9)}\n")
