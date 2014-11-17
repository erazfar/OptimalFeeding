from Equations import *

from decimal import *
import collections
import math
import numpy as np

import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def simulate(lst):
	# unbox lst struct
	start_day = lst["start_day"]
	end_day = lst["end_day"]
	diff = lst["diff"]
	food_cost = lst["food_cost"]
	facility_cost = lst["facility_cost"]
	animal_price = lst["animal_price"]
	extend_days = lst["extend_days"]

	#calculate discount/day from given discount/yr
	discount = lst["r_value"]/Decimal(365)	

	# generate lookup tables for max size and rates at each day
	max_sizes = build_max_size_array(lst["start_day"], lst["end_day"])
	max_rates = build_max_rate_array(max_sizes)
	print max_sizes

	# get min/start size, max/end size and calculate number of sizes
	start_size = max_sizes[start_day]
	max_size = max_sizes[end_day]

	# repeat end size for each extend day
	for i in range(extend_days):
		max_sizes[end_day+Decimal(1)+i] = max_size

	# generate the graph with infinity for each value
	graph = {}

	# from start_day to end_day,
	#	construct a dict for each day then size
	for curr_day in range(start_day, end_day+extend_days+Decimal(1)):
		curr_day = Decimal(curr_day)
		graph[curr_day] = {}
		# print curr_day

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
	for curr_day in range(start_day, end_day+extend_days):
		curr_day = Decimal(curr_day)
		# print curr_day
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

			# get max size and rates based on the first day
			#	s.t. the max is >= the current size
			curr_max_size = size_by_size_max_feeding(curr_size, max_sizes)
			curr_min_size = curr_size

			# count the number of possible sizes
			num_next_sizes = (curr_max_size - curr_size) / diff

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
			if num_next_sizes == 0:
				slope = 0 # never used, just a placeholder
			else:
				slope = (curr_max_rate - curr_min_rate) / num_next_sizes
				slope *= curr_discount
			
			# set up next size and current cost (edge weight)
			curr_next_size = curr_size
			curr_next_cost = curr_cost + curr_min_rate*curr_discount

			# for every next possible weight
			for i in range(num_next_sizes+Decimal(1)):
			
				# get the next size's current min cost
				next_cost = next_day_min_costs[curr_next_size]

				# if this cost is less than the current min, swap
				if curr_next_cost < next_cost:
					next_day_min_costs[curr_next_size] = curr_next_cost

				# increment for the next iteration
				curr_next_cost += slope
				curr_next_size += diff

			# increment for next size iteration
			curr_size += diff

	print ("day, size, kg_food, feeding_cost, profit")
	for k,v in graph[end_day+extend_days].items():
		revenue = get_revenue(start_day, discount, animal_price, end_day+extend_days, k)
		total_cost = food_cost * v
		rent_cost = 0 # facility_cost * (end_day - start_day)
		profit = revenue - total_cost - rent_cost
		if (extend_days > Decimal(0)):
			Pa = animal_price
			Pl = animal_price
			oc = opportunity_cost(Pa, max_size, end_day-start_day+Decimal(1),
				Pl, k, end_day+extend_days, discount)
			profit -= oc
		print ("%d, %f, %f, %f, %f" % (end_day+extend_days, k, v, total_cost, profit))

	return graph

# by default, set end_day to 80
def main(end_day=5, extend_days=3):
	lst = {
		"start_day": Decimal(1),
		"end_day": end_day,
		"animal_price":Decimal(2.89),
		"food_cost":Decimal(0.25),
		"facility_cost":Decimal(0.35),
		"r_value":Decimal(0.075),
		"diff": Decimal(0.1),
		"extend_days": Decimal(extend_days)
	}
	return simulate(lst)

if __name__ == "__main__":
	main()