import math
from decimal import *
import collections

#from Functions import day_by_size_max_feeding;

ONEPLACES = Decimal('0.1');


## ad-lib function
def max_size_by_day(day):
    '''
    day = Decimal(day);
    size = Decimal('562.959283') / (Decimal('1.0') + Decimal(math.exp(Decimal('-1') * (day - Decimal('398.095995')) / Decimal('189.503378'))));
    size = size.quantize(ONEPLACES);
    return size;
    '''
    
    day = Decimal(day)
    size = Decimal('343.822718') + Decimal('1.8290907') * day
    size = size.quantize(ONEPLACES)
    return size;


## max feeding rate function
## return Decimal variable with 10 digits
## 10 digits probably not prices enough need to check with the information 
def max_feeding_rate(size):
    ## getcontext.prec is to set all Decimal variable to total 10 digits.
    '''
    getcontext().prec = 10;
    size = Decimal(size);
    Q = Decimal('1.004226945') + Decimal('0.0176380855')*(size); ##check value
    return Q;
    '''
    getcontext().prec = 10;
    size = Decimal(size)
    Q = Decimal(4.33209573) + Decimal(0.00562646041)* size ##check value
    return Q

## min feeding rate function    
def feeding_rate(day_diff, size):
    getcontext().prec = 10;
    day_diff = Decimal(day_diff)
    size = Decimal(size)
    c = Decimal('0.032566835') * Decimal(pow(size, Decimal('0.75')));
    ##print ("c:", c)
    a = max_feeding_rate(size) - c;
    ## CAUTIOUS: NEED TO UPDATE THE day_on_adlib function
    ##print ("a:", a)
    expo = Decimal(math.exp(Decimal('-1') * Decimal('0.032882286') * day_diff));
    ##print ("expo", expo)
    Q = a * expo + c;
    return Q;
    
    
def opportunity_cost(Pa, Sa, Ta, Pl, Sl, Tl, discount):
    profit = Pa * Sa
    N = 30
    part1 = Decimal(1/Decimal(math.exp(discount*Ta)-1))
    part1 = part1 - Decimal(Decimal(math.exp(-1*(N+1)*discount*Ta))/Decimal(1-math.exp(-1*discount*Ta)))
    part2 = Decimal(1/Decimal(math.exp(discount*Tl)-1))
    part2 = part2 - Decimal(Decimal(math.exp(-1*(N+1)*discount*Tl))/Decimal(1-math.exp(-1*discount*Tl)))
    dis = profit * (part1-part2)
    return dis;
    

def discount_factor_value(day, discount):
    value = Decimal(math.exp(Decimal(-1) * discount * (day)))
    return value

def get_revenue(start_day, discount, sell_price, w_day, w_size):    
    day_diff = (w_day) - start_day;
    gain = sell_price * (w_size) * discount_factor_value(w_day, discount)
    return gain
    
def build_facililty_array(cost_array, discount, start_day, end_day):
    facility_array = {}
    for today in range(start_day, end_day + Decimal('1')):
        diff = today - start_day
        today_cost = cost_array[Decimal(today)] * discount_factor_value(diff,discount)
        if diff==0 :
            facility_array[Decimal(today)] = today_cost
        else :
            facility_array[Decimal(today)] = today_cost + facility_array[Decimal(today)-Decimal('1')]
    return facility_array
    
    ############################DO NOT NEED TO MODIFY##################
    
def build_max_rate_array(max_sizes):
    max_rate_array = {};
    
    for day,size in max_sizes.items():
        max_rate_array[day] = max_feeding_rate(size)

    return max_rate_array

def build_max_size_array(start_day, end_day):
    max_size_array = {};
    
    for today in range(start_day, end_day + 1):
        max_size_array[Decimal(today)] = max_size_by_day(Decimal(today))
    max_size_array = collections.OrderedDict(sorted(max_size_array.items()))
    return max_size_array
    
##need to check the correctness of the logic
def day_by_size_max_feeding(size,max_size_array):
    for today in max_size_array:
        if(max_size_array[today] >= size):
        #and today <= end_day):
               return today;
    print 'error in day_by_size_max_feeding'
    return -1;



##input size and get the size by max feeding
def size_by_size_max_feeding(size, max_size_array):
    size = Decimal(size);
    ##getcontext().prec = 6;
    for today in max_size_array:
        if (max_size_array[today] >= size):
            # and today <= (end_day)):
            ## finding the slope of current day ##
            tempint = (max_size_array[(today+Decimal(1))] - max_size_array[(today)]);
            
            return (size + tempint).quantize(ONEPLACES)
    print 'error in size_by_size_max_feeding'
    return -1



    
