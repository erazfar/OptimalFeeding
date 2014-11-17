'''
src: http://stackoverflow.com/questions/12423601
'''

from Main import *

import numpy as np
from mayavi import mlab

def drawSurface(graph):

	X = []
	Y = []
	Z = []

	# create points for each day/size/cost in graph
	for i in range(len(graph)):
		ith = graph[i]
		for j in range(len(ith)):
			jth = ith[j]
			X.append(float(jth.day))
			Y.append(float(jth.size))
			Z.append(float(ith[j].min_cost))

	pts = mlab.points3d(X, Y, Z, Z)

	mlab.xlabel("time")
	mlab.ylabel("size")
	mlab.zlabel("cost")
	mlab.show()

if __name__ == "__main__":
	if (len(sys.argv) == 2):
		g = main(int(sys.argv[1]))
	elif (len(sys.argv) >= 3):
		g = main(int(sys.argv[1]), int(sys.argv[2]))
	else:
		g = main()
	drawSurface(g)