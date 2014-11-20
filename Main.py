from Equations import *

import sys
import os
import collections
import math
import numpy as np
import csv

# writes the facility cost per day to a CSV file
def write_facility_cost_csv(facility_cost, start_day, end_day):
	file_name = 'facility_cost_output.csv'
	writer = csv.writer(open(file_name, 'wb'), delimiter=',')
	for i in range (start_day, end_day+1):
		writer.writerow([str(i), str(facility_cost)]) #change to access array indexs after csv input implemented

# writes the food cost per day to a CSV file
def write_food_cost_csv(food_cost, start_day, end_day):
	file_name = 'food_cost_output.csv'
	writer = csv.writer(open(file_name, 'wb'), delimiter=',')
	for i in range (start_day, end_day+1):
		writer.writerow([str(i), str(food_cost)]) #change to access array indexs after csv input implemented

#writes the final weight and price to a CSV file
def write_animal_weight_csv(animal_weight, animal_price, end_day):
	file_name = 'animal_weight_output.csv'
	writer = csv.writer(open(file_name, 'wb'), delimiter=',')
	writer.writerow([str(animal_weight), str(animal_price[end_day-1])])

# loads the animal_price.csv values into the animal_price list
def load_animal_price_csv(lst):
	print "Loading animal_price CSV"
	animal_price_array = [0 for  i in range(lst["start_day"], lst["end_day"] + 1) ]
	with open('animal_price.csv', 'rb') as csvfile:
		csvreader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
		i = 0
		for row in csvreader:
			curr_row = row[0].split(',')
			animal_price_array[i] = float(curr_row[1])
			i += 1
			if i > lst["end_day"] - 1:
				break
	return animal_price_array

#loads the facility_cost.csv values into the facility_cost list
def load_facility_cost_csv(lst):
	print "Loading facility_cost CSV"
	facility_cost_array = [0 for  i in range(lst["start_day"], lst["end_day"] + 1) ]
	with open('facility_cost.csv', 'rb') as csvfile:
		csvreader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
		i = 0
		for row in csvreader:
			curr_row = row[0].split(',')
			facility_cost_array[i] = float(curr_row[1])
			i += 1
			if i > lst["end_day"] - 1:
				break
	return facility_cost_array

# calculates total facility costs based on the starting day, ending day, and cost per day
def calculate_facility_costs(lst):
	facility_cost_array = lst["facility_cost"]
	total_cost = 0
	for i in range(lst["start_day"], lst["end_day"]):
		total_cost += facility_cost_array[i]
	return total_cost

class Node(object):
	def __init__(self, day, size, min_cost=float("inf"), days_const=0):
		self.day = day
		self.size = size		
		self.min_cost = min_cost
		self.min_food = 0.
		self.min_edge = 0.
		self.days_const = days_const
		self.prev_node = None

def simulate(lst):
	# unbox lst struct
	start_day = (lst["start_day"])
	end_day = lst["end_day"]	
	food_costs = lst["food_costs"]	
	facility_costs = lst["facility_costs"]
	prices_per_kg = lst["prices_per_kg"]
	extend_days = lst["extend_days"]

	# if the given food costs is a single value, create a dict for every day
	if not isinstance(food_costs, list):
		food_costs = build_const_food_cost_array(start_day, end_day+extend_days, food_costs)

	# if the given facility costs is a single value, create a dict for every day
	if not isinstance(facility_costs, list):
		facility_costs = build_const_facility_cost_array(start_day, end_day+extend_days, facility_costs)

	#calculate discount/day from given discount/yr
	discount = lst["r_value"]/365.	

	# generate lookup tables for max size at each day
	max_sizes = build_max_size_array(start_day, end_day)

	size_by_size_lookup = build_size_by_size_lookup(start_day, end_day, max_sizes)
	day_by_size_lookup = build_day_by_size_lookup(start_day, end_day, max_sizes)

	# get min/start size, max/end size and calculate number of sizes
	start_size = max_sizes[start_day]
	max_size = max_sizes[end_day]
	total_num_sizes = max_size - start_size + 1

	# if the given prices per kg is a single value, create a dict for every day
	if not isinstance(prices_per_kg, list):
		prices_per_kg = build_const_prices_per_kg_array(start_size, total_num_sizes, prices_per_kg)

	# repeat end size for each extend day
	for i in range(extend_days):
		max_sizes[end_day+1+i] = max_size

	# init the graph structure with the initial day's mincost set to zero
	graph = { start_day : { start_size : { 0 : Node(start_day, start_size, min_cost=0.) } } }

	# iterate through each day except the last
	for curr_day in range(start_day, end_day+extend_days):

		next_day = curr_day+1
		print("Calculating costs for day: %d" % (curr_day))

		# calculate number of reachable sizes
		curr_size = start_size
		end_size = max_sizes[curr_day]
		next_end_size = max_sizes[next_day]
		num_sizes = next_end_size - start_size + 1

		# create empty column for the next day which will be replaced with min costs				
		graph[next_day] = {}
		next_day_min_costs = graph[next_day]
		
		curr_size = start_size
		while curr_size <= next_end_size:
			next_day_min_costs[curr_size] = {}
			next_size_min_costs = next_day_min_costs[curr_size]
			num_days_const = next_day - day_by_size_lookup[curr_size]
			if (curr_size == start_size):
				days_const = next_day - start_day
				next_size_min_costs[days_const] = Node(next_day, curr_size, days_const=days_const)
			else:
				for days_const in range(num_days_const+1):
					next_size_min_costs[days_const] = Node(next_day, curr_size, days_const=days_const)

			curr_size += 1
		
		# cache the column lookups for this day and the next
		curr_day_min_costs = graph[curr_day]
		next_day_min_costs = graph[next_day]

		# cache the current day facility and food costs
		curr_facility_cost = facility_costs[curr_day]
		curr_food_cost = food_costs[curr_day]

		# from start to max size that day
		for curr_size, curr_days_const in curr_day_min_costs.items():
			
			for curr_day_const, curr_node in curr_days_const.items():

				# get the precalculated min cost to this size on this day
				curr_cost = curr_node.min_cost + curr_facility_cost

				# get the first day s.t. its max size is >= the current size
				max_size_day = day_by_size_lookup[curr_size]

				# get max size and rates based on the first day
				#	s.t. the max is >= the current size
				curr_max_size = size_by_size_lookup[curr_size]
				curr_min_size = curr_size

				# count the number of possible sizes
				# num_next_sizes = get_num_sizes(curr_max_size, curr_size, diff)
				num_next_sizes = curr_max_size - curr_size + 1

				# calculate the minimum feeding cost based on the day diff
				curr_min_rate = feeding_rate(curr_node.days_const, curr_size/10.)

				# calculate the max feeding rate based on current size
				curr_max_rate = max_feeding_rate(curr_size/10.)

				# calculate current discount rate
				curr_discount = discount_factor_value(curr_day - start_day, discount)

				# linearly approximate the feed cost depending on the min and max
				#	feeding rates
				if num_next_sizes == 1:
					cost_step = 0 # never used, just a placeholder
				else:
					slope = (curr_max_rate - curr_min_rate) / (num_next_sizes - 1)
					cost_step = curr_food_cost * slope * curr_discount
				
				# set up next size and current cost (edge weight)
				curr_next_size = curr_size
				curr_next_rate = curr_min_rate
				curr_next_cost = curr_cost + curr_food_cost*curr_min_rate*curr_discount

				# for every next possible weight
				for next_node in range(num_next_sizes):
					
					# if the current node is staying the same size,
					#	point edge to the next number of days constant
					if curr_size == curr_next_size:
						next_day_const = curr_day_const + 1
					else:
						next_day_const = 0
					next_node = next_day_min_costs[curr_next_size][next_day_const]
					next_cost = next_node.min_cost

					# if this cost is less than the current min, swap vals
					if curr_next_cost < next_cost:
						next_node.min_cost = curr_next_cost
						next_node.prev_node = curr_node
						next_node.min_edge = (curr_next_cost - curr_cost)
						next_node.min_food = curr_node.min_food + curr_next_rate # *curr_discount

					# increment for the next iteration
					curr_next_rate += slope
					curr_next_cost += cost_step
					curr_next_size += 1

	print ("day, size, kg_food, feeding_cost, profit, day_cost, prev_node_size")

	# cache the last column in the graph, i.e. the column of nodes on the final day
	final_day_column = graph[end_day+extend_days]
	final_day_column = collections.OrderedDict(sorted(final_day_column.items()))

	# iterate over each element
	for curr_size, curr_days_const in final_day_column.items():
		for curr_day_const, curr_node in curr_days_const.items():

			# calculate profit based on revenue and total expenses
			revenue = get_revenue(start_day, discount, prices_per_kg[curr_node.size], curr_node.day, curr_node.size/10.)
			profit = revenue - curr_node.min_cost

			# extend_days is greater than zero, calculate and subtract the
			#	opportunity cost
			if (extend_days > 0):
				Pa = prices_per_kg[curr_node.size]
				Pl = prices_per_kg[curr_node.size]
				oc = opportunity_cost(Pa, max_size, end_day-start_day+1,
					Pl, curr_node.size, curr_node.day, discount)
				profit -= oc
			print ("%d, %d, %f, %f, %f, %f, %f, %f" % (curr_node.day, curr_node.days_const, curr_node.size/10., curr_node.min_food, curr_node.min_cost, profit, curr_node.min_edge, curr_node.prev_node.size/10.))

	# write_animal_weight_csv(max_sizes[end_day], animal_price, end_day)
	# write_food_cost_csv(food_cost, start_day, end_day)
	# write_facility_cost_csv(facility_cost, start_day, end_day)
	return graph

# by default, set end_day to 80
def main(start_day=1, end_day=80, extend_days=0):
	lst = {
		"start_day": start_day,
		"end_day": end_day,
		"prices_per_kg":2.89,
		"food_costs":0.25, #need to implement variable food cost
		"facility_costs":0.35,
		"r_value":0.075,
		"extend_days": extend_days
	}

	# check if animal_price and facility_cost CSV files are provided for use
	# if os.path.isfile('animal_price.csv'):
	# 	lst["animal_price"] = load_animal_price_csv(lst)
	# if os.path.isfile('facility_cost.csv'):
	#  	lst["facility_cost"] = load_facility_cost_csv(lst)

	g = simulate(lst)
	return g

if __name__ == "__main__":
	if (len(sys.argv) == 3):
		main(int(sys.argv[1]), int(sys.argv[2]))
	elif (len(sys.argv) >= 4):
		main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
	else:
		main()