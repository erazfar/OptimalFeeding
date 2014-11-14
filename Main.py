from Equations import *

from decimal import *
import collections
import math
import numpy as np

# class Node(object):
# 	def __init__(self):
# 		self.min_cost = float("inf")

# 	def get_min_cost():
# 		return min_cost

# 	def set_min_cost(cost):
# 		self.min_cost = cost

# 	def update_min_cost(cost):
# 		if (cost < min_cost):
# 			min_cost = cost

def get_x(day):
	return int(day) - 1

def get_y(curr_size, start_size, max_size, diff):
	if (curr_size == start_size):
		return 0
	else:
		return int( (curr_size - start_size)/(max_size - start_size)/diff )

def main(lst):
	diff = Decimal(0.1)
	max_sizes = build_max_size_array(lst["start_day"], lst["end_day"])
	max_rates = build_max_rate_array(max_sizes)
	start_day = lst["start_day"]
	end_day = lst["end_day"]
	start_size = max_sizes[start_day]
	max_size = max_sizes[end_day]
	num_sizes = (max_sizes[end_day] - max_sizes[start_day]) / diff + Decimal(1)
	# print(num_sizes)
	graph = [ [ Decimal("Infinity") for j in range(num_sizes) ] for i in range(lst["end_day"])]
	graph[0][0] = Decimal(0)
	# print np.arange(float(start_size), float(max_size), 0.1)[0]

	for curr_day in range(start_day, end_day):
		curr_day = Decimal(curr_day)
		print curr_day
		curr_size = start_size
		end_size = max_sizes[curr_day]
		while curr_size <= end_size:		
			curr_size = Decimal(curr_size)
			curr_x = get_x(curr_day)
			curr_y = get_y(curr_size, start_size, end_size, diff)
			curr_cost = graph[curr_x][curr_y]

			max_size_day = day_by_size_max_feeding(curr_size, max_sizes)
			num_next_sizes = (max_sizes[max_size_day+Decimal(1)] - max_sizes[max_size_day]) / diff
			# print num_next_sizes
			curr_max_size = max_sizes[max_size_day]
			curr_max_rate = max_rates[max_size_day]
			### ??? ###
			day_diff = curr_day - day_by_size_max_feeding(curr_size, max_sizes);
			curr_min_rate = feeding_rate(day_diff, curr_size)
			slope = (curr_max_rate - curr_min_rate) / (num_next_sizes - Decimal(1))

			counter = 0
			curr_next_size = curr_size
			curr_next_cost = curr_cost + curr_min_rate
			print("%d: %f: %d" % (curr_day, curr_size, num_next_sizes))
			while counter < num_next_sizes:
				next_x = get_x(curr_day+Decimal(1))
				next_y = get_y(curr_next_size, start_size, max_size, diff)
				next_cost = graph[next_x][next_y]
				if curr_next_cost < next_cost:
					graph[next_x][next_y] = Decimal(curr_next_cost)

				curr_next_cost += slope
				curr_next_size += diff
				counter += 1

			curr_size += diff
	print graph[9]
if __name__ == "__main__":
	lst = {"start_day": Decimal(1),
		"end_day": Decimal(10),
		"animal_price":Decimal(2.89),
		"food_cost":Decimal(0.25),
		"facility_cost":Decimal(0.35),
		"r_value":Decimal(0.075)}

	main(lst)