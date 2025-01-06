# configurable-algo-NRP
Project focused on configurable algorithm using CP solvers for Nurse rostering problem
![Tests](https://github.com/Efnalim/configurable-algo-NRP/actions/workflows/tests.yml/badge.svg)

## Prerequisites
- installed Cplex from [link](https://www.ibm.com/products/ilog-cplex-optimization-studio/cplex-optimizer)
- python 3.9


## Installation
1. Before installing, change the path in `requirements.txt` to the right python package contaning Cplex Python API. 
2. Run this command to install dependencies: 
```
pip install -r requirements.txt
```
3. Run any script from the `benchmark` folder to try the implemented solvers.

## Tests
to run tests
```
 pytest --no-header -v --cov=src\nsp_solver\validator --cov=src\nsp_solver\simulator --cov=src\nsp_solver\solver\nsp_cplex.py
```