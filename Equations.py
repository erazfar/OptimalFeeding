import math
import collections

#from Functions import day_by_size_max_feeding;

## ad-lib function
def max_size_by_day(day):
    '''
    day = (day);
    size = ('562.959283') / (('1.0') + (math.exp(('-1') * (day - ('398.095995')) / ('189.503378'))));
    size = size.quantize(ONEPLACES);
    return size;
    '''

    # size = (562.959283) / ((1.0) + (math.exp((-1) * (day - (398.095995)) / (189.503378))));
    size = 343.822718 + 1.8290907 * day
    return int(round(size*10.))


## max feeding rate function
## return Decimal variable with 10 digits
## 10 digits probably not prices enough need to check with the information 
def max_feeding_rate(size):
    ## getcontext.prec is to set all Decimal variable to total 10 digits.
    '''
    getcontext().prec = 10;
    size = (size);
    Q = ('1.004226945') + ('0.0176380855')*(size); ##check value
    return Q;
    # '''

    Q = 4.33209573 + 0.00562646041 * size
    return Q

## min feeding rate function    
def feeding_rate(day_diff, size):
    c = 0.032566835 * pow(size, 0.75);
    a = max_feeding_rate(size) - c;
    ## CAUTIOUS: NEED TO UPDATE THE day_on_adlib function
    expo = math.exp(-1 * 0.032882286 * day_diff);
    Q = a * expo + c;
    return Q
    
def opportunity_cost(Pa, Sa, Ta, Pl, Sl, Tl, discount):
    profit = Pa * Sa
    N = 30
    part1 = 1/(math.exp(discount*Ta)-1)
    part1 = part1 - math.exp(-1*(N+1)*discount*Ta)/(1-math.exp(-1*discount*Ta))
    part2 = (1/(math.exp(discount*Tl)-1))
    part2 = part2 - math.exp(-1*(N+1)*discount*Tl)/(1-math.exp(-1*discount*Tl))
    dis = profit * (part1-part2)
    return dis
    

def discount_factor_value(day, discount):
    value = math.exp(-1. * discount * day)
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
    
    ############################DO NOT NEED TO MODIFY##################
    

def build_max_size_array(start_day, end_day):
    max_size_array = {};
    
    for today in range(start_day, end_day + 1):
        max_size_array[today] = max_size_by_day(today)
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



    
