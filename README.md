# configurable-algo-NRP
Project focused on configurable algorithm using CP solvers for Nurse rostering problem
![Tests](https://github.com/Efnalim/configurable-algo-NRP/actions/workflows/tests.yml/badge.svg)

| day | psani | -/√ | dalsi  | -/√ | dalsi                      | -/√ |
| --- | ----- | --- | ------ | --- | -------------------------- | --- |
| Po  | 8 str | √   | essay  | √   | testy pro HC ve validatoru | -   |
| Ut  | 8 str | -   | ODV-hw | √   | testy pro SC ve validatoru | -   |
| St  | 8 str |     |        |     | docs and readme            | -   |
| Ct  | 8 str |     |        |     |                            |     |


to run tests pytest --no-header -v --cov=src\nsp_solver\validator --cov=src\nsp_solver\simulator --cov=src\nsp_solver\solver\nsp_cplex.py