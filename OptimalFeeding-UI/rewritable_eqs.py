import math

class RewritableEqs(object):

    get_adlib_time = lambda self, size : (size - 343.822718) / 1.8291

    get_adlib_size = lambda self, time : 343.822718 + time*1.8291

    get_adlib_rate = lambda self, size : 4.33209573 + 0.00562646041 * size

    def get_surface_rate(self, time, size):
        qo = self.get_adlib_rate(size)
        c = 0.032566835*size**0.75
        a = qo - c
        to = self.get_adlib_time(size)
        q = a * math.exp(-0.032882286*(time - to)) + c
        return q

    def get_comp_rate(self, time, size):
        next_adlib_size = self.get_adlib_size(time+1)
        adlib_size = self.get_adlib_size(time)
        adlib_rate = self.get_adlib_rate(adlib_size)
        
        m = -.807225
        comp_rate = (m*(float(size)/adlib_size - 1) + 1)
        comp_rate *= (next_adlib_size-adlib_size)/adlib_rate
        return comp_rate

    def get_comp_max_size(self, time, size):
        no_comp_max_size = self.get_next_max_size(time, size)
        no_comp_max_rate = self.get_surface_rate(time+1, no_comp_max_size)
        comp_rate = self.get_comp_rate(time, size)
        comp_max_size = comp_rate*no_comp_max_rate+size
        return comp_max_size

    def get_adj_rate(self, time, size, wo, w, n): # without cg, with cg, next sizes
        diff = (n - size)/(w - size)
        pre_size = diff*(wo - size)+size
        return self.get_surface_rate(get_surface_rate(time+1,pre_size))

    def get_next_max_size(self, size):
        return self.get_adlib_size(self.get_adlib_time(size)+1)

    def get_next_max_size_restr(self, size, restr):
        return size + (self.get_adlib_size(self.get_adlib_time(size)+1) - size)*(1 - restr)

    def f2i(self, f):
        return int(round(f*10))

    def i2f(self, i):
        return i/10.

    def get_adlib_schedule(self, sim_len):
        x = range(2,sim_len+1)
        y = [self.f2i(self.get_adlib_size(i))/10. for i in x]
        z = [self.get_surface_rate(time, size) for time,size in zip(x, y)]
        return zip(x,y,z)

    def get_adlib_profit(self, sim_len):
        x = range(2,sim_len+1)
        y = [self.f2i(self.get_adlib_size(i))/10. for i in x]
        z = [self.get_surface_rate(time, size) for time,size in zip(x, y)]
        return y[-1]*2.89 - 0.25*sum(z)

    def get_plot_point(self, time, size):
        adlib_size = self.get_adlib_size(time+2)
        if size - adlib_size > 0.05:
            return None
        else:
            return self.get_surface_rate(time, size)