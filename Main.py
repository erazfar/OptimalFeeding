from Equations import *

import sys
import collections
import math
import numpy as np
import csv

# transforms the given day to the x-coordinate of the graph
def get_x(day, start_day):
	return day-start_day

# undoes the above transform
def get_x_inv(x, start_day):
	return x + start_day

# transforms the given size to the y-coordinate of the graph
def get_y(size, start_size, diff):
	return int(round((size - start_size)/diff))

# undoes the above transform
def get_y_inv(y, start_size, diff):
	return round(diff*y + start_size, 1)

# returns the # of sizes between the given max and min, both inclusive
def get_num_sizes(max_size, min_size, diff):
	return int(round((max_size - min_size)/diff)) + 1

# writes the facility cost per day to a CSV file
def write_facility_cost_csv(facility_cost, start_day, end_day):
	file_name = 'facility_cost.csv'
	writer = csv.writer(open(file_name, 'wb'), delimiter=',')
	for i in range (start_day, end_day+1):
		writer.writerow([str(i), str(facility_cost)]) #change to access array indexs after csv input implemented

# writes the food cost per day to a CSV file
def write_food_cost_csv(food_cost, start_day, end_day):
	file_name = 'food_cost.csv'
	writer = csv.writer(open(file_name, 'wb'), delimiter=',')
	for i in range (start_day, end_day+1):
		writer.writerow([str(i), str(food_cost)]) #change to access array indexs after csv input implemented

#writes the final weight and price to a CSV file
def write_animal_weight_csv(animal_weight, animal_price):
	file_name = 'animal_weight.csv'
	writer = csv.writer(open(file_name, 'wb'), delimiter=',')
	writer.writerow([str(animal_weight), str(animal_price)])


class Node(object):
	def __init__(self, day, size, min_cost=float("inf")):
		self.day = day
		self.size = size		
		self.min_cost = min_cost
		self.min_edge = 0.
		self.prev_node = None

def simulate(lst):
	# unbox lst struct
	start_day = lst["start_day"]
	end_day = lst["end_day"]
	# diff = lst["diff"]
	diff = 0.1
	food_cost = lst["food_cost"]
	facility_cost = lst["facility_cost"]
	animal_price = lst["animal_price"]
	extend_days = lst["extend_days"]

	#calculate discount/day from given discount/yr
	discount = lst["r_value"]/365.	

	# generate lookup tables for max size at each day
	max_sizes = build_max_size_array(start_day, end_day)

	# get min/start size, max/end size and calculate number of sizes
	start_size = max_sizes[start_day]
	max_size = max_sizes[end_day]

	# repeat end size for each extend day
	for i in range(extend_days):
		max_sizes[end_day+1+i] = max_size

	# init the graph structure with the initial day's mincost set to zero
	graph = [ [Node(start_day, start_size, 0.)] ]

	# iterate through each day except the last
	for curr_day in range(start_day, end_day+extend_days):

		curr_day = curr_day
		print("Calculating costs for day: %d" % (curr_day))

		# calculate number of reachable sizes
		curr_size = start_size
		end_size = max_sizes[curr_day]
		next_end_size = max_sizes[curr_day+1]
		num_sizes = get_num_sizes(next_end_size, start_size, diff)

		# create empty column for the next day which will be replaced with min costs		
		graph.append( [Node(curr_day+1, get_y_inv(i, start_size, diff)) for i in range(num_sizes)] )
		
		# cache the column lookups for this day and the next
		curr_x = get_x(curr_day, start_day)
		curr_day_min_costs = graph[curr_x]
		next_day_min_costs = graph[curr_x+1]

		# from start to max size that day
		while curr_size <= end_size:
			curr_size = curr_size

			# get the precalculated min cost to this size on this day
			curr_y = get_y(curr_size, start_size, diff)
			curr_node = curr_day_min_costs[curr_y]
			curr_cost = curr_node.min_cost

			# get the first day s.t. its max size is >= the current size
			max_size_day = day_by_size_max_feeding(curr_size, max_sizes)

			# get max size and rates based on the first day
			#	s.t. the max is >= the current size
			curr_max_size = size_by_size_max_feeding(curr_size, max_sizes)
			curr_min_size = curr_size

			# count the number of possible sizes
			num_next_sizes = get_num_sizes(curr_max_size, curr_size, diff) # int(round((curr_max_size - curr_size)/ diff))

			# count the days between current and the max size day
			day_diff = curr_day - max_size_day

			# calculate the minimum feeding cost based on the day diff
			curr_min_rate = feeding_rate(day_diff, curr_size)

			# calculate the max feeding rate based on current size
			curr_max_rate = max_feeding_rate(curr_size)

			# calculate current discount rate
			curr_discount = discount_factor_value(curr_day - start_day, discount)

			# linearly approximate the feed cost depending on the min and max
			#	feeding rates
			if num_next_sizes == 1:
				slope = 0 # never used, just a placeholder
			else:
				slope = (curr_max_rate - curr_min_rate) / num_next_sizes
				slope *= curr_discount
			
			# set up next size and current cost (edge weight)
			curr_next_size = curr_size
			curr_next_cost = curr_cost + curr_min_rate*curr_discount

			# for every next possible weight
			for i in range(num_next_sizes):
			
				# get the next size's current min cost
				next_y = get_y(curr_next_size, start_size, diff)
				next_node = next_day_min_costs[next_y]
				next_cost = next_node.min_cost

				# if this cost is less than the current min, swap vals
				if curr_next_cost < next_cost:
					next_node.min_cost = curr_next_cost
					next_node.prev_node = curr_node
					next_node.min_edge = (curr_next_cost - curr_cost)/curr_discount					

				# increment for the next iteration
				curr_next_cost += slope
				curr_next_size += diff

			# increment for next size iteration
			curr_size += diff
			curr_size = round(curr_size, 1)

	print ("day, size, kg_food, feeding_cost, profit, day_cost, prev_node_size")

	# cache last column in graph
	last_column = graph[int(end_day + extend_days - start_day)]

	# iterate over each element
	for i in range(len(last_column)):
		# cache current node	
		curr_node = last_column[i]

		# calculate profit based on revenue and total expenses
		revenue = get_revenue(start_day, discount, animal_price, curr_node.day, curr_node.size)
		rent_cost = 0 # facility_cost * (end_day - start_day)
		total_cost = food_cost * curr_node.min_cost + rent_cost
		profit = revenue - total_cost

		# extend_days is greater than zero, calculate and subtract the
		#	opportunity cost
		if (extend_days > 0):
			Pa = animal_price
			Pl = animal_price
			oc = opportunity_cost(Pa, max_size, end_day-start_day+1,
				Pl, curr_node.size, curr_node.day, discount)
			profit -= oc
		print ("%d, %f, %f, %f, %f, %f, %f" % (curr_node.day, curr_node.size, curr_node.min_cost, total_cost, profit, curr_node.min_edge, curr_node.prev_node.size))

	write_animal_weight_csv(max_sizes[end_day], animal_price)
	write_food_cost_csv(food_cost, start_day, end_day)
	write_facility_cost_csv(facility_cost, start_day, end_day)
	return graph

# by default, set end_day to 80
def main(start_day=1, end_day=80, extend_days=0):
	lst = {
		"start_day": start_day,
		"end_day": end_day,
		"animal_price":2.89,
		"food_cost":0.25,
		"facility_cost":0.35,
		"r_value":0.075,
		"extend_days": extend_days
	}
	g = simulate(lst)
	return g

if __name__ == "__main__":
	if (len(sys.argv) == 3):
		main(int(sys.argv[1]), int(sys.argv[2]))
	elif (len(sys.argv) >= 4):
		main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
	else:
		main()
