from Equations import *

import sys
import os
import collections
import math
import numpy as np
import csv

class Node(object):
	def __init__(self, day, size, min_cost=float("inf"), days_const=0):
		self.day = day
		self.size = size		
		self.min_cost = min_cost
		self.min_food = 0.
		self.min_edge = 0.
		self.days_const = days_const
		self.prev_node = None

	def copy_from(self, node):
		self.day = node.day
		self.size = node.size		
		self.min_cost = node.min_cost
		self.min_food = node.min_food
		self.min_edge = node.min_edge
		self.days_const = node.days_const
		self.prev_node = node.prev_node

class Simulation(object):
	def __init__(self, start_day, end_day, extend_days, food_costs, facility_costs, prices_per_kg, r_value, cycles_per_year):
		self.start_day = start_day
		self.end_day = end_day
		self.extend_days = extend_days
		self.food_costs = food_costs
		self.facility_costs = facility_costs
		self.prices_per_kg = prices_per_kg
		self.discount = r_value
		self.cycles_per_year = cycles_per_year

	def get_optimal_path(self):
		graph = self.graph
		start_day = self.start_day
		end_day = self.end_day
		extend_days = self.extend_days
		discount = self.discount
		prices_per_kg = self.prices_per_kg

		# cache the last column in the graph, i.e. the column of nodes on the final day
		final_day_column = graph[end_day+extend_days]

		max_profit_node = None
		max_profit = float('inf')
		# iterate over each element
		for curr_size, curr_days_const in final_day_column.items():
			for curr_day_const, curr_node in curr_days_const.items():
				if curr_node.profit < max_profit:
					max_profit_node = curr_node
					max_profit = curr_node.profit

		X = []
		Y = []
		while curr_node.prev_node != None:
			X.append(curr_node.day-1)
			Y.append(curr_node.min_food - curr_node.prev_node.min_food)
			curr_node = curr_node.prev_node

		return (X,Y)

	def get_surface_points(self):
		graph = self.graph

		X = []
		Y = []
		Z = []

		for day,sizes in graph.items():
			for size,days_const in sizes.items():
				days_const, node = sorted(days_const.items())[-1]
				X.append(day)
				Y.append(size/10.)
				Z.append(node.min_rate)

		return (X,Y,Z)

	
	def simulate(self):
		# unbox lst struct
		start_day = self.start_day
		real_end_day = self.end_day
		end_day = self.end_day+self.extend_days
		extend_days = self.extend_days
		discount = self.discount
		cycles_per_year = self.cycles_per_year

		# if the given food costs is a single value, create a dict for every day
		if not isinstance(self.food_costs, list):
			self.food_costs = build_const_food_cost_array(start_day, end_day, self.food_costs)
		food_costs = self.food_costs

		# if the given facility costs is a single value, create a dict for every day
		if not isinstance(self.facility_costs, list):
			self.facility_costs = build_const_facility_cost_array(start_day, end_day, self.facility_costs)
		facility_costs = self.facility_costs

		# generate lookup tables for max size at each day
		max_sizes = build_max_size_array(start_day, end_day)
		size_by_size_lookup = build_size_by_size_lookup(start_day, end_day, max_sizes)
		day_by_size_lookup = build_day_by_size_lookup(start_day, end_day, max_sizes)

		# get min/start size, max/end size and calculate number of sizes
		start_size = max_sizes[start_day]
		max_size = max_sizes[end_day]
		total_num_sizes = max_size - start_size + 1

		# if the given prices per kg is a single value, create a dict for every day
		if not isinstance(self.prices_per_kg, list):
			self.prices_per_kg = build_const_prices_per_kg_array(start_size, total_num_sizes, self.prices_per_kg)
		prices_per_kg = self.prices_per_kg

		# init the graph structure with the initial day's mincost set to zero
		graph = { start_day : { start_size : { 0 : Node(start_day, start_size, min_cost=0.) } } }

		# iterate through each day except the last
		for curr_day in range(start_day, end_day):

			next_day = curr_day+1
			print("Calculating costs for day: %d" % curr_day)

			# calculate number of reachable sizes
			curr_size = start_size
			
			if curr_day < end_day:
				end_size = max_sizes[curr_day]
				next_end_size = max_sizes[next_day]
			else:
				end_size = max_sizes[end_day]
				next_end_size = end_size
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

					# calculate the minimum feeding cost based on the day diff
					curr_min_rate = feeding_rate(curr_node.days_const, curr_size/10.)
					curr_node.min_rate = curr_min_rate

					# calculate the max feeding rate based on current size
					curr_max_rate = max_feeding_rate(curr_size/10.)
					curr_comp_rate = get_comp_rate(curr_size/10., curr_max_size/10., max_sizes[curr_day]/10., curr_max_rate)
					curr_max_size = int(round(curr_max_rate*curr_comp_rate*10.))+curr_size

					# count the number of possible sizes
					# num_next_sizes = get_num_sizes(curr_max_size, curr_size, diff)
					num_next_sizes = curr_max_size - curr_size + 1

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

						if curr_next_size > max_size:
							continue
						
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
							next_node.min_food = curr_node.min_food + curr_next_rate

						# increment for the next iteration
						curr_next_rate += slope
						curr_next_cost += cost_step
						curr_next_size += 1

		# cache the last column in the graph, i.e. the column of nodes on the final day
		final_day_column = graph[end_day]
		final_day_column = collections.OrderedDict(sorted(final_day_column.items()))
		
		final_size = max_sizes[real_end_day]
		ad_lib_node = graph[real_end_day][final_size][0]
		ad_lib_profit = get_revenue(start_day, discount, prices_per_kg[final_size], real_end_day, final_size/10.)
		ad_lib_profit -= ad_lib_node.min_cost

		opp_cost = opportunity_cost(cycles_per_year, discount, real_end_day - start_day + 1,
			end_day - start_day + 1, ad_lib_profit)

		# iterate over each element
		for curr_size, curr_days_const in final_day_column.items():
			if curr_size > final_size:
				break
			for curr_day_const, curr_node in curr_days_const.items():
				curr_node.min_rate = feeding_rate(curr_node.days_const, curr_size/10.)

				if (extend_days > 0 and curr_size == final_size):
					earlier_node = graph[curr_node.day - curr_node.days_const][curr_node.size][0]
					curr_node.copy_from(earlier_node)
					curr_node.opp_cost = opportunity_cost(cycles_per_year, discount, real_end_day - start_day + 1,
						curr_node.day - start_day + 1, ad_lib_profit)
				else:
					curr_node.opp_cost = opp_cost

				# calculate profit based on revenue and total expenses
				revenue = get_revenue(start_day, discount, prices_per_kg[curr_node.size], curr_node.day, curr_node.size/10.)
				profit = revenue - curr_node.min_cost
				profit += curr_node.opp_cost
				
				curr_node.revenue = revenue
				curr_node.profit = profit

		self.graph = graph
		self.final_size = final_size
		return

	def print_end_costs(self):		
		graph = self.graph
		start_day = self.start_day
		end_day = self.end_day
		extend_days = self.extend_days
		discount = self.discount
		prices_per_kg = self.prices_per_kg

		# cache the last column in the graph, i.e. the column of nodes on the final day
		final_day_column = graph[end_day+extend_days]
		final_day_column = collections.OrderedDict(sorted(final_day_column.items()))

		# print ("day, days_const, size, kg_food, feeding_cost, profit, day_cost, prev_node_size")
		print ("day, days_const, size, kg_food, min_cost, revenue, opp_cost, profit, prev_size")

		final_output = []

		# iterate over each element
		for curr_size, curr_days_const in final_day_column.items():
			if curr_size > self.final_size:
				break
			for curr_day_const, curr_node in curr_days_const.items():
				print ("%d, %d, %f, %f, %f, %f, %f, %f, %f" % (curr_node.day, curr_node.days_const, curr_node.size/10., curr_node.min_food, curr_node.min_cost, curr_node.revenue, curr_node.opp_cost, curr_node.profit, curr_node.prev_node.size/10.))
