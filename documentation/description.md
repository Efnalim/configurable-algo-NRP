# Description of constrains 
## Hard constraints
### HC1 - Single assignment per day	
    Each nurse can be assigned to at most one shift per day.
### HC2 - Under-staffing	
	Each shift and each skill has a minimal number of nurses that must be assigned each day of the week.
### HC3 - Shift type successions	
	The shift-type assignments of one nurse in two consecutive days must belong to the legal successions provided in the scenario. 
### HC4 - Missing required skill
	A shift of a given skill must necessarily be fulfilled by a nurse having that skill.
### HC5 - Consecutive assignments
	The minimum and maximum number of consecutive assignments, per shift or global, must be respected.
### HC6 - Consecutive days off
	The minimum and maximum number of consecutive days off must be respected.
### HC7 - Maximum incomplete week-ends
	Every nurse that has the complete weekend value set to true, must work both week-end days or none. Maximum of incomplete weekends must be respected
### HC8 - Total assignments: 
	For each nurse the total number of assignments (working days) must be included within the limits (minimum and maximum) enforced by her/his contract.
### HC9: - Minimal continuous free period
	Each nurse must have every week a minimum continuous free period.
### HC10 - Single assignment per day - exception	
    Each nurse can be assigned to at most one shift per day or she can be assigned to early and night shift on the same day.
<!-- ### HC11 - Missing required skill - exception
	A shift of a given skill must necessarily be fulfilled by a nurse having that skill or by a nurse that can be assigned to this shift with this skill "if needed". -->
### HC11 - Maximum shifts of specific type (night) due to health condition
	Each nurse with a specific health condition (pregnancy) must not be assigned to a shift of specific type (night) more than maximum.
### HC12 - Planned vacation
	Each planned vacation (1 week long) must be respected.

## Soft constraints
### SC1 - Insufficient staffing for optimal coverage
	The number of nurses for each shift for each skill must be equal to the optimal requirement. Each missing nurse is penalized according to the weight provided (30). Extra nurses above the optimal value are not considered in the cost.
### SC2 - Consecutive assignments - optimal
	The minimum and maximum number of consecutive assignments, per shift or global, should be respected. Their evaluation involves also the border data. Each extra or missing day is multiplied by the corresponding weight. The weights for violation of consecutive shift constraints and consecutive working days are respectively 15 and 30.
### SC3 - Consecutive days off - optimal
	The minimum and maximum number of consecutive days off should be respected. Their evaluation involves also the border data. Each extra or missing day is multiplied by weight (30).
### SC4 - Assignement preferences
	Each assignment to an undesired shift is penalized by weight (10).
### SC5 - Complete week-end optimal
	Every nurse that has the complete weekend value set to true, must work both week-end days or none. If she/he works only one of the two days Sat and Sun this is penalized by weight (30). 
### SC6 - Total assignments - optimal 
	For each nurse the total number of assignments (working days) must be included within the limits (minimum and maximum) enforced by her/his contract. The difference (in either direction), multiplied by its weight (20), is added to the objective function.
### SC7 - Total weekends - optimal 
	For each nurse the total number of assignments during weekends must be included within the limits (maximum) enforced by her/his contract. The difference, multiplied by its weight (30), is added to the objective function.
### SC8 - Using "if needed" skill
	If nurse is assigned to a shift with a skill in category "if needed" each such shift penalized by weight (15)
### SC9 - Overtime preferences
	Unsatisfied preferences for overtime (each month) are penalized by weight (10). Each assignment missing from desired overtime is penalized by weight (10).
------------------------------------------------------------------------------------------------------------------------------------------------

## A Hybrid Approach for Solving Real-World Nurse Rostering Problems [link](https://link.springer.com/chapter/10.1007/978-3-642-23786-7_9)
## INRC-II [link](https://mobiz.vives.be/inrc2/wp-content/uploads/2014/10/INRC2.pdf)
