from Equations import *

from decimal import *
import collections
import math
import numpy as np

def simulate(lst):
	# unbox lst struct
	start_day = lst["start_day"]
	end_day = lst["end_day"]
	diff = lst["diff"]

	# generate lookup tables for max size and rates at each day
	max_sizes = build_max_size_array(lst["start_day"], lst["end_day"])
	max_rates = build_max_rate_array(max_sizes)

	# get min/start size, max/end size and calculate number of sizes
	start_size = max_sizes[start_day]
	max_size = max_sizes[end_day]
	num_sizes = (max_sizes[end_day] - max_sizes[start_day]) / diff + Decimal(1)

	# generate the graph with infinity for each value
	graph = {}

	# from start_day to end_day,
	#	construct a dict for each day then size
	for curr_day in range(start_day, end_day+Decimal(1)):
		curr_day = Decimal(curr_day)
		graph[curr_day] = {}
		print curr_day

		# from curr_size to end_size for this current day,
		#	set the min_cost to infinity
		curr_size = start_size
		end_size = max_sizes[curr_day]
		while curr_size <= end_size:
			curr_size = Decimal(curr_size)
			graph[curr_day][curr_size] = Decimal("Infinity")
			curr_size += diff

	# reset the minimum cost for the initial day to zero
	graph[Decimal(1)][start_size] = Decimal(0)

	# iterate through each day except the last
	for curr_day in range(start_day, end_day):
		curr_day = Decimal(curr_day)
		print curr_day
		curr_size = start_size
		end_size = max_sizes[curr_day]
		next_day_min_costs = graph[curr_day+1]

		# from start to max size that day
		while curr_size <= end_size:
			curr_size = Decimal(curr_size)

			# get the precalculated min cost to this size on this day
			curr_cost = graph[curr_day][curr_size]

			# get the first day s.t. its max size is >= the current size
			max_size_day = day_by_size_max_feeding(curr_size, max_sizes)

			# count the number of possible sizes
			'''
			This is likely to be changed; via past year's RunSimulation lines 92-101:
			They appear to linearly approximate between the min and the max,
				but the max is simply the first max >= the current weight.
			Also, they use the day_diff in the min feeding cost equation
				(as do we for now) but this assumes there has
				been day_diff days held constant at that weight, 
				which is usually not true.
			'''
			num_next_sizes = (max_sizes[max_size_day+Decimal(1)] - max_sizes[max_size_day]) / diff

			# get max size and rates based on the first day
			#	s.t. the max is >= the current size
			curr_max_size = max_sizes[max_size_day]
			curr_max_rate = max_rates[max_size_day]

			# count the days between current and the max size day
			day_diff = curr_day - max_size_day

			# calculate the minimum feeding cost based on the day diff
			curr_min_rate = feeding_rate(day_diff, curr_size)

			# linearly approximate the feed cost depending on the min and max
			#	feeding rates
			slope = (curr_max_rate - curr_min_rate) / (num_next_sizes - Decimal(1))

			# set up the counter, current next size and current cost (edge weight)
			counter = 0
			curr_next_size = curr_size
			curr_next_cost = curr_cost + curr_min_rate

			# for every next possible weight
			while counter < num_next_sizes:
			
				# get the next size's current min cost
				next_cost = graph[curr_day+Decimal(1)][curr_next_size]
			
				# if this cost is less than the current min, swap
				if curr_next_cost < next_cost:
					next_day_min_costs[curr_next_size] = Decimal(curr_next_cost)

				# increment for the next iteration
				curr_next_cost += slope
				curr_next_size += diff
				counter += 1

			# increment for next size iteration
			curr_size += diff
	
	return graph

# by default, set end_day to 80
def main(end_day=80):
	lst = {
		"start_day": Decimal(1),
		"end_day": end_day,
		"animal_price":Decimal(2.89),
		"food_cost":Decimal(0.25),
		"facility_cost":Decimal(0.35),
		"r_value":Decimal(0.075),
		"diff": Decimal(0.1)
	}
	return simulate(lst)

if __name__ == "__main__":
	main()