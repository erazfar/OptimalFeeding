import collections

# from Equations import *
from rewritable_eqs import RewritableEqs

class Node(object):

    def __init__(self, time, size, rate, min_cost=float("inf"), min_feed=float("inf")):
        self.time = time
        self.size = size
        self.rate = rate
        self.min_cost = min_cost
        self.min_feed = min_feed
        self.prev_size = None
        self.prev_feed = None

class Simulation(object):

    def __init__(self, sim_len, restr_len=0, restr=0.):
        self.eqs =  RewritableEqs()
        self.sim_len = sim_len
        self.restr_len = restr_len
        self.feed_cost = 0.25
        self.facility_cost = 0.35
        self.market_price = 2.89
        self.discount = 0.075
        self.restr = restr

    def start(self):

        eqs = self.eqs

        self.nodes = []
        
        start_time = 1
        start_size = eqs.f2i(eqs.get_adlib_size(1))
        graph = { start_time : { start_size : Node(start_time, start_size/10., eqs.get_surface_rate(start_time, start_size/10.), 0., 0.) } }

        for time in range(start_time+1, self.sim_len+1):
            graph[time] = {}
            max_size = eqs.f2i(eqs.get_adlib_size(time))
            
            for size in range(start_size, max_size+1):              
                graph[time][size] = Node(time,size/10., eqs.get_surface_rate(time, size/10.))
                self.nodes.append(graph[time][size])

        self.graph = graph

    def get_feeding_schedule(self, time, size):
        node = self.graph[time][size]
        if node.prev_size == None:
            return []
        else:
            return self.get_feeding_schedule(time-1, node.prev_size) + [(time,node.size,node.rate)]

    def get_optimal_schedule(self):
        max_profit_size = self.start_size
        max_profit = self.graph[self.sim_len][self.start_size].profit
        
        for size,node in self.graph[self.sim_len].items():
            if node.profit > max_profit:
                max_profit_size = size
                max_profit = node.profit

        return self.get_feeding_schedule(self.sim_len, max_profit_size)

    def find_paths(self):

        eqs = self.eqs

        graph = self.graph

        start_time = 1
        start_size = eqs.f2i(eqs.get_adlib_size(1))
        self.start_size = start_size

        for time in range(start_time, self.sim_len):
            max_size = eqs.f2i(eqs.get_adlib_size(time))
            
            for size in range(start_size, max_size+1):
                node = graph[time][size]
                min_cost = node.min_cost
                min_feed = node.min_feed
                
                if (time <= self.restr_len):
                    next_max_size = eqs.f2i(eqs.get_next_max_size_restr(size/10., self.restr))
                else:
                    if size == max_size:
                        next_max_size = eqs.f2i(eqs.get_adlib_size(time+1))
                    else:
                        next_max_size = eqs.f2i(eqs.get_next_max_size(size/10.))
                
                for next_size in range(size,next_max_size+1):
                    next_node = graph[time+1][next_size]
                    temp_feed = next_node.rate
                    temp_cost = self.feed_cost*temp_feed + min_cost

                    if next_node.min_cost > temp_cost:
                        next_node.min_cost = temp_cost
                        next_node.prev_size = size
                        next_node.min_feed = min_feed + temp_feed

    def calculate_profits(self):

        eqs = self.eqs

        final_day = self.graph[self.sim_len]
        adlib_profit = eqs.get_adlib_profit(self.sim_len)
        self.graph[self.sim_len] = collections.OrderedDict(sorted(final_day.items()))
        first_unreachable_size = None

        for size,node in self.graph[self.sim_len].items():
            if node.min_cost == float("inf"):
                first_unreachable_size = size
                break

            node.revenue = node.size*self.market_price
            node.profit = node.revenue - node.min_cost
            premium = (adlib_profit + node.min_cost)/node.size
            node.premium_diff = premium - self.market_price
            node.premium_percent = premium / self.market_price - 1.

        end_size = eqs.f2i(eqs.get_adlib_size(self.sim_len))
        if first_unreachable_size is not None:
            for size in range(first_unreachable_size, end_size+1):
                del self.graph[self.sim_len][size]


    def print_final_day(self):

        print("day, size, feed, cost, revenue, profit, premium-, premium%")
        for size,node in self.graph[self.sim_len].items():
            print("%d, %f, %f, %f, %f, %f, %f, %f, %f" % (node.time, node.size, node.min_feed, node.min_cost, node.revenue, node.profit, node.premium_diff, node.premium_percent, node.prev_size/10.))

    def print_schedule(self, schedule):
        for day in schedule:
            print day

    def run_complete(self):
        self.start()
        self.find_paths()
        self.calculate_profits()        