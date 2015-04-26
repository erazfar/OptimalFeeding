import math

def get_adlib_time(size):
    # return -190*math.log(563-size_zero) + 190*math.log(size_zero) + 398
    return (size - 343.822718) / 1.8291
    # return (size - 345.66) / 1.83

def get_adlib_size(time):
    return 343.822718 + time*1.8291

def get_adlib_rate(size):
    # return 1 + 0.018*size
    return 4.33209573 + 0.00562646041 * size

def get_surface_rate(time, size):
    qo = get_adlib_rate(size)
    c = 0.032566835*size**0.75
    a = qo - c
    to = get_adlib_time(size)
    q = a * math.exp(-0.032882286*(time - to)) + c
    return q

def get_comp_rate(time, size):
    # next_adlib_size = f2i(get_adlib_size(time+1))/10.
    # adlib_size = f2i(get_adlib_size(time))/10.
    next_adlib_size = get_adlib_size(time+1)
    adlib_size = get_adlib_size(time)
    adlib_rate = get_adlib_rate(adlib_size)
    
    m = -.807225
    comp_rate = (m*(float(size)/adlib_size - 1) + 1)
    comp_rate *= (next_adlib_size-adlib_size)/adlib_rate
    return comp_rate

def get_comp_max_size(time, size):
    no_comp_max_size = get_next_max_size(time, size)
    no_comp_max_rate = get_surface_rate(time+1, no_comp_max_size)
    comp_rate = get_comp_rate(time, size)
    comp_max_size = comp_rate*no_comp_max_rate+size
    return comp_max_size

def get_adj_rate(time, size, wo, w, n): # without cg, with cg, next sizes
    diff = (n - size)/(w - size)
    pre_size = diff*(wo - size)+size
    return get_surface_rate(get_surface_rate(time+1,pre_size))

def get_next_max_size(size):
    return get_adlib_size(get_adlib_time(size)+1)

def get_next_max_size_restr(size, restr):
    return size + (get_adlib_size(get_adlib_time(size)+1) - size)*(1 - restr)

def f2i(f):
    return int(round(f*10))

def i2f(i):
    return i/10.

def get_adlib_schedule(sim_len):
    x = range(2,sim_len+1)
    y = [f2i(get_adlib_size(i))/10. for i in x]
    z = [get_surface_rate(time, size) for time,size in zip(x, y)]
    return zip(x,y,z)

def get_adlib_profit(sim_len):
    x = range(2,sim_len+1)
    y = [f2i(get_adlib_size(i))/10. for i in x]
    z = [get_surface_rate(time, size) for time,size in zip(x, y)]
    return y[-1]*2.89 - 0.25*sum(z)