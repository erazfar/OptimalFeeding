import math
import collections

# returns the max rate affected by the compensatory weight gain / feed calculation
def get_comp_rate(curr_size, next_max_size, ad_lib_size, ad_lib_rate):
    m = -.807225
    comp_rate = (m*(float(curr_size)/ad_lib_size - 1) + 1) * (next_max_size - curr_size)/ad_lib_rate
    return comp_rate

# returns the max rate affected by the compensatory weight gain / feed calculation
def get_comp_factor(curr_size, next_max_size, ad_lib_size, ad_lib_rate):
    m = -.807225
    comp_rate = (float(curr_size)/ad_lib_size - 1)*m + 1
    return comp_rate

## ad-lib function
def max_size_by_day(day):
    size = 343.822718 + 1.8290907 * day
    return size

## max feeding rate function
## return Decimal variable with 10 digits
def max_feeding_rate(size):
    Q = 4.33209573 + 0.00562646041 * size
    return Q

## min feeding rate function    
def feeding_rate(day_diff, size):
    day_diff += 1 # TODO: determine if this is correct!
    c = 0.032566835 * pow(size, 0.75);
    a = max_feeding_rate(size) - c;
    expo = math.exp(-1 * 0.032882286 * day_diff);
    Q = a * expo + c;
    return Q
    
def opportunity_cost(cycles_per_year, discount, ad_lib_day, limit_day, ad_lib_profit):
    r = discount
    N = cycles_per_year
    Tl = limit_day
    Ta = ad_lib_day
    OC = -1 * ad_lib_profit * ( (1/(math.exp(r/365*Ta)-1) - (math.exp(-1*(N/r+1)*r/365*Ta))/(1-math.exp(-1*r/365*Ta)) )
                            - (1/(math.exp(r/365*Tl)-1) - (math.exp(-1*(N/r+1)*r/365*Tl))/(1-math.exp(-1*r/365*Tl)) ) )
    return OC

def discount_factor_value(day, discount):
    value = math.exp(-1 * discount/365. * day)
    return value

def get_revenue(start_day, discount, sell_price, w_day, w_size):    
    day_diff = (w_day) - start_day;
    gain = sell_price * (w_size) * discount_factor_value(w_day, discount)
    return gain
    
def build_facililty_array(cost_array, discount, start_day, end_day):
    facility_array = {}
    for today in range(start_day, end_day + 1):
        diff = today - start_day
        today_cost = cost_array[today] * discount_factor_value(diff,discount)
        if diff==0 :
            facility_array[today] = today_cost
        else :
            facility_array[today] = today_cost + facility_array[today-1]
    return facility_array

def build_max_size_array(start_day, end_day):
    max_size_array = {};
    
    for today in range(start_day, end_day + 1):
        max_size_array[today] = int(round(max_size_by_day(today)*10.))
    max_size_array = collections.OrderedDict(sorted(max_size_array.items()))
    return max_size_array

def build_const_food_cost_array(start_day, end_day, food_cost):
    return {i : food_cost for i in range(start_day, end_day+1)}

def build_const_facility_cost_array(start_day, end_day, facility_cost):
    return {i : facility_cost for i in range(start_day, end_day+1)}

def build_const_prices_per_kg_array(start_size, num_sizes, price_per_kg):
    return { start_size + i : price_per_kg for i in range(num_sizes+1)}
    

def build_day_by_size_lookup(start_day, end_day, max_sizes):
    day_by_size_lookup = {}
    start_size = max_sizes[start_day]
    end_size = max_sizes[end_day]
    curr_size = start_size
    while curr_size <= end_size:
        day_by_size_lookup[curr_size] = day_by_size_max_feeding(curr_size, max_sizes)        
        curr_size += 1
    return day_by_size_lookup

def build_size_by_size_lookup(start_day, end_day, max_sizes):
    size_by_size_lookup = {}
    start_size = max_sizes[start_day]
    end_size = max_sizes[end_day-1]
    curr_size = start_size
    while curr_size <= end_size:
        size_by_size_lookup[curr_size] = size_by_size_max_feeding(curr_size, max_sizes)        
        curr_size += 1
    return size_by_size_lookup

##need to check the correctness of the logic
def day_by_size_max_feeding(size,max_size_array):
    ret = None
    for today in max_size_array:
        if(max_size_array[today] >= size):
               ret = today
               break
    return ret

##input size and get the size by max feeding
def size_by_size_max_feeding(size, max_size_array):
    ret = None
    for today in max_size_array:
        if (max_size_array[today] >= size):
            ## finding the slope of current day ##
            tempint = (max_size_array[today+1] - max_size_array[today]);
            return size + tempint
            break
    return ret