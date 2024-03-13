# Description of cosntrains
## INRC-II
### Hard constrains
#### H1 - Single assignment per day	
Each nurse can be assigned to at most one shift per day.
#### H2 - Under-staffing	
	Each shift and each skill has a minimal number of nurses that must be assigned each day of the week. 
#### H3 - Shift type successions	
	The shift-type assignments of one nurse in two consecutive days must belong to the legal successions provided in the scenario. 
#### H4 - Missing required skill
	A shift of a given skill must necessarily be fulfilled by a nurse having that skill.

### Soft constrains
#### S1 - Insufficient staffing for optimal coverage
	The number of nurses for each shift for each skill must be equal to the optimal requirement. Each missing nurse is penalized according to the weight provided (30). Extra nurses above the optimal value are not considered in the cost.
#### S2 - Consecutive assignments
	The minimum and maximum number of consecutive assignments, per shift or global, should be respected. Their evaluation involves also the border data. Each extra or missing day is multiplied by the corresponding weight. The weights for violation of consecutive shift constraints and consecutive working days are respectively 15 and 30.
#### S3 - Consecutive days off
	The minimum and maximum number of consecutive days off should be respected. Their evaluation involves also the border data. Each extra or missing day is multiplied by weight (30).
#### S4 - Preferences
	Each assignment to an undesired shift is penalized by weight (10).
#### S5 - Complete week-end
	Every nurse that has the complete weekend value set to true, must work both week-end days or none. If she/he works only one of the two days Sat and Sun this is penalized by weight (30).
