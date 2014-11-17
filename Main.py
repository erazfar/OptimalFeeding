from Equations import *

from decimal import *
import collections
import math
import numpy as np

# transforms the given day to the x-coordinate of the graph
def get_x(day, start_day):
	return int(day-start_day)

# undoes the above transform
def get_x_inv(x, start_day):
	return Decimal(x) + start_day

# transforms the given size to the y-coordinate of the graph
def get_y(size, start_size, diff):
	return int((size - start_size)/diff)

# undoes the above transform
def get_y_inv(y, start_size, diff):
	return diff*Decimal(y) + start_size

# returns the # of sizes between the given max and min, both inclusive
def get_num_sizes(max_size, min_size, diff):
	return int((max_size - min_size)/diff + 1)

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

	# get min/start size, max/end size and calculate number of sizes
	start_size = max_sizes[start_day]
	max_size = max_sizes[end_day]

	# repeat end size for each extend day
	for i in range(extend_days):
		max_sizes[end_day+Decimal(1)+i] = max_size

	# init the graph structure with the initial day's mincost set to zero
	graph = [ [Decimal(0) ]

	# iterate through each day except the last
	for curr_day in range(start_day, end_day+extend_days):
		curr_day = Decimal(curr_day)
		print("Calculating costs for day: %d" % (curr_day))

		curr_size = start_size
		end_size = max_sizes[curr_day]
		next_end_size = max_sizes[curr_day+1]

		# create empty column for the next day which will be replaced with min costs
		graph.append( [Decimal("Infinity")]*get_num_sizes(next_end_size, start_size, diff) )
		
		# cache the column lookups for this day and the next
		curr_x = get_x(curr_day, start_day)
		curr_day_min_costs = graph[curr_x]
		next_day_min_costs = graph[curr_x+1]

		# from start to max size that day
		while curr_size <= end_size:
			curr_size = Decimal(curr_size)

			# get the precalculated min cost to this size on this day
			# curr_cost = graph[curr_day][curr_size]
			curr_y = get_y(curr_size, start_size, diff)
			curr_cost = curr_day_min_costs[curr_y]

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
				next_y = get_y(curr_next_size, start_size, diff)
				next_cost = next_day_min_costs[next_y]

				# if this cost is less than the current min, swap
				if curr_next_cost < next_cost:
					next_day_min_costs[next_y] = curr_next_cost

				# increment for the next iteration
				curr_next_cost += slope
				curr_next_size += diff

			# increment for next size iteration
			curr_size += diff

	print ("day, size, kg_food, feeding_cost, profit")
	# for k,v in graph[end_day+extend_days].items():
	last_column = graph[int(end_day + extend_days - 1)]
	for i in range(len(last_column)):
		# v = get_y_inv(last_column[i], start_size, diff)
		v = last_column[i]
		k = get_y_inv(i, start_size, diff)
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
def main(end_day=50, extend_days=0):
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