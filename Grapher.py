'''
src: http://stackoverflow.com/questions/12423601
'''

from Main import *


import numpy as np
from mayavi import mlab
import matplotlib.pyplot as plt

def draw_min_cost_surface(graph):

	graph = sim.graph

	X = []
	Y = []
	Z = []

	for day,sizes in graph.items():
		for size,days_const in sizes.items():
			days_const, node = sorted(days_const.items())[0]
			X.append(day)
			Y.append(size/10.)
			Z.append(node.min_cost)

	pts = mlab.points3d(X, Y, Z, Z)

	mesh = mlab.pipeline.delaunay2d(pts)

	# Remove the point representation from the plot
	pts.remove()

	# Draw a surface based on the triangulation
	surf = mlab.pipeline.surface(mesh)

	mlab.xlabel("time")
	mlab.ylabel("size")
	mlab.zlabel("cost")
	mlab.show()

def draw_min_feed_surface(graph):

	graph = sim.graph

	X = []
	Y = []
	Z = []

	for day,sizes in graph.items():
		for size,days_const in sizes.items():
			days_const, node = sorted(days_const.items())[-1]
			X.append(day)
			Y.append(size/10.)
			Z.append(node.min_rate*10)
	
	# for i in range(len(X)):
	# 	print ("%d,%f,%f" % (X[i], Y[i], Z[i]))

	pts = mlab.points3d(X, Y, Z, Z)

	mesh = mlab.pipeline.delaunay2d(pts)

	# Remove the point representation from the plot
	pts.remove()

	# Draw a surface based on the triangulation
	surf = mlab.pipeline.surface(mesh)

	mlab.xlabel("time")
	mlab.ylabel("size")
	mlab.zlabel("rate")
	mlab.show()

def plot_optimal_path(sim):

	days,cost = sim.get_optimal_path()
	fig = plt.figure()
	plt.scatter(days, cost)
	plt.show()

if __name__ == "__main__":
	if (len(sys.argv) == 3):
		sim = main(int(sys.argv[1]), int(sys.argv[2]))
	elif (len(sys.argv) >= 4):
		sim = main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
	else:
		sim = main()

	plot_optimal_path(sim)
	draw_min_cost_surface(sim)
	draw_min_feed_surface(sim)