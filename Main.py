from Equations import *
from Simulation import *

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

# by default, set end_day to 80
def main(start_day=1, end_day=80, extend_days=0, price_per_kg=0.25, food_cost=0.35, facility_cost=2.89, r_value=0.075, cycles_per_year=2, restriction=0.1):

	sim = Simulation(start_day, end_day, extend_days, price_per_kg, food_cost, facility_cost, r_value, cycles_per_year, restriction)
	sim.simulate()
	sim.print_end_costs()
	return sim

if __name__ == "__main__":
	
	if (len(sys.argv) == 3):
		sim = main(int(sys.argv[1]), int(sys.argv[2]))
	elif (len(sys.argv) >= 4):
		sim = main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
	else:
		sim = main()