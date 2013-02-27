minimize courses: d1+d2+d3

Subject To
	cond1: a1  - 32a2 + 0a3 + 0a4  + 0a5=0
	cond2: 0a1 +  1a2 - 1a3 + 0a4  + 0a5=0
	cond3: 0a1 +  0a2 + 1a3 - 1a4  + 0a5=0
	cond4: 0a1 +  0a2 + 0a3 + 32a4 - a5=0

Bounds
	1 <= a1
	1 <= a2
	1 <= a3
	1 <= a4
	1 <= a5

Integer
	a1
	a2
	a3
	a4
	a5
