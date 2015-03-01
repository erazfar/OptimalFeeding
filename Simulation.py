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
		self.min_curr_food = 0.

	def copy_from(self, node):
		self.day = node.day
		self.size = node.size		
		self.min_cost = node.min_cost
		self.min_food = node.min_food
		self.min_edge = node.min_edge
		self.days_const = node.days_const
		self.prev_node = node.prev_node

	def pp(self):
		curr_node = self
		print ("%d, %d, %f, %f, %f, %f" % (curr_node.day, curr_node.days_const, curr_node.size/10., curr_node.min_curr_food, curr_node.min_food, curr_node.min_cost))

class Simulation(object):
	def __init__(self, start_day, end_day, extend_days, food_costs=0.25, facility_costs=0.35, prices_per_kg=2.89, r_value=0.075, cycles_per_year=2, restriction=0.0):
		self.start_day = start_day
		self.end_day = end_day
		self.extend_days = extend_days
		self.food_costs = food_costs
		self.facility_costs = facility_costs
		self.prices_per_kg = prices_per_kg
		self.discount = r_value
		self.cycles_per_year = cycles_per_year
		self.restriction = restriction

	def ad_lib_node(self):
		self.start_day = start_day

	def get_feeding_schedule(self, node):
		curr_node = node.prev_node

		X = []
		Y = []

		while curr_node != None:
			X.append(curr_node.day)
			Y.append(curr_node.min_curr_food)
			curr_node = curr_node.prev_node

		X.reverse()
		Y.reverse()
		return (X,Y)

	def get_optimal_end_node(self):
		graph = self.graph
		end_day = self.end_day
		extend_days = self.extend_days

		# cache the last column in the graph, i.e. the column of nodes on the final day
		final_day_column = graph[end_day+extend_days]

		max_profit_node = None
		max_profit = float('-inf')
		# iterate over each element
		for curr_size, curr_days_const in final_day_column.items():
			for curr_day_const, curr_node in curr_days_const.items():
				if curr_node.profit > max_profit:
					max_profit_node = curr_node
					max_profit = curr_node.profit

		return max_profit_node

	def get_optimal_feeding_schedule(self):
		optimal_node = self.get_optimal_end_node()
		return self.get_feeding_schedule(optimal_node)

	def get_optimal_path(self):
		return get_optimal_feeding_schedule()

	def get_path(self, node):
		nodes = []
		curr_node = node
		while curr_node != None:
			nodes.append(curr_node)
			curr_node = curr_node.prev_node
		nodes.reverse()
		return nodes

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
		restriction = 1. - self.restriction

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
		end_size = max_sizes[real_end_day]
		total_num_sizes = end_size - start_size + 1

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

			# create empty column for the next day which will be replaced with min costs				
			graph[next_day] = {}
			next_day_min_costs = graph[next_day]
			
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
					if curr_day == 1:
						print curr_min_rate
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

					if curr_day < real_end_day:
						num_next_sizes = int(round((size_by_size_lookup[curr_size] - curr_size)*restriction)) + 1
					elif curr_max_size > end_size:
						num_next_sizes = (end_size - curr_size) + 1
					
					# set up next size and current cost (edge weight)
					curr_next_size = curr_size
					curr_next_rate = curr_min_rate
					curr_next_cost = curr_cost + curr_food_cost*curr_min_rate*curr_discount

					# for every next possible weight
					for next_node in range(num_next_sizes):

						if curr_next_size > end_size:
							break
						
						# if the current node is staying the same size,
						#	point edge to the next number of days constant
						if curr_size == curr_next_size:
							next_day_const = curr_day_const + 1
						else:
							next_day_const = 0

						if curr_next_size not in next_day_min_costs:
							next_day_min_costs[curr_next_size] = {}

						if next_day_const not in next_day_min_costs[curr_next_size]:
							next_day_min_costs[curr_next_size][next_day_const] = Node(next_day, curr_next_size, days_const=next_day_const)

						next_node = next_day_min_costs[curr_next_size][next_day_const]
						next_cost = next_node.min_cost

						# if this cost is less than the current min, swap vals
						if curr_next_cost < next_cost:
							next_node.min_cost = curr_next_cost
							next_node.prev_node = curr_node
							next_node.min_edge = (curr_next_cost - curr_cost)
							next_node.min_food = curr_node.min_food + curr_next_rate							
							next_node.min_curr_food = curr_next_rate

						# increment for the next iteration
						curr_next_rate += slope
						curr_next_cost += cost_step
						curr_next_size += 1

		# cache the last column in the graph, i.e. the column of nodes on the final day
		final_day_column = graph[end_day]
		final_day_column = collections.OrderedDict(sorted(final_day_column.items()))
		
		final_size = max_sizes[real_end_day]
		# ad_lib_node = graph[real_end_day][final_size][0]
		# ad_lib_profit = get_revenue(start_day, discount, prices_per_kg[final_size], real_end_day, final_size/10.)
		# ad_lib_profit -= ad_lib_node.min_cost
		ad_lib_profit = 0.

		opp_cost = opportunity_cost(cycles_per_year, discount, real_end_day - start_day + 1,
			end_day - start_day + 1, ad_lib_profit)

		# iterate over each element
		for curr_size, curr_days_const in final_day_column.items():

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

	def print_nodes(self, array):
		for n in array:
			n.pp()

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

		print ("day, days_const, size, kg_food, min_cost, revenue, opp_cost, profit, prev_size")

		final_output = []

		# iterate over each element
		for curr_size, curr_days_const in final_day_column.items():

			for curr_day_const, curr_node in curr_days_const.items():
				print ("%d, %d, %f, %f, %f, %f, %f, %f, %f" % (curr_node.day, curr_node.days_const, curr_node.size/10., curr_node.min_food, curr_node.min_cost, curr_node.revenue, curr_node.opp_cost, curr_node.profit, curr_node.prev_node.size/10.))
