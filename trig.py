import math

def heading(p0x, p0y, p1x, p1y, p2x, p2y):
	return math.atan2(
		 (p1x-p0x)+(p2x-p1x),
		-(p1y-p0y)-(p2y-p1y)
		 )

print(heading(0,0,0,1,.5,2))