import sqlite3
from flask import *
import simulation
from equations import *

import plotly.plotly as py
import plotly.tools as tls   
from plotly.graph_objs import *

import math

# Database config

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('OF_SETTINGS', silent=True)


@app.route('/')
def index(name = None):
    return render_template("index.html")

@app.route('/', methods = ['POST'])
def index_post(name = None):
    if(request.method == 'POST'):

        sim_len = int(request.form.get('sim_len', 80, type=int))
        restr_len = int(request.form.get('restr_len', 50, type=int))
        restr = float(request.form.get('restr', 9, type=float)) / 100
        price_per_kg = float(request.form.get('market_price', 2.89, type=float))
        food_cost = float(request.form.get('feed_cost', 0.25, type=float))
        facility_cost = float(request.form.get('fac_cost', 0.35, type=float))
        r_value = int(request.form.get('int_rate', 7.5, type=float)) / 100

        sim = simulation.Simulation(sim_len, restr_len, restr)
        sim.run_complete()

        graph_url = get_graph_url(sim)

        print "plot url: ", graph_url
        return render_template("output.html", ploturl = graph_url)

def get_plot_point(time, size):
    adlib_size = get_adlib_size(time+2)
    if size - adlib_size > 0.05:
        return None
    else:
        return get_surface_rate(time, size)

def get_graph_url(sim):
    sim_len = sim.sim_len
    start_size = f2i(get_adlib_size(1))
    end_size = f2i(get_adlib_size(sim_len))

    x = range(1, sim_len+1)
    y = [float(i)/10. for i in range(start_size, end_size+1)]
    z = [ [ get_plot_point(time, size) for time in x] for size in y]

    trace1 = Surface(
        z=z,  # link the fxy 2d numpy array
        x=x,  # link 1d numpy array of x coords
        y=y   # link 1d numpy array of y coords
    )

    adlib_x, adlib_y, adlib_z = zip(*get_adlib_schedule(sim_len))

    trace2 = Scatter3d(
        x=adlib_x,
        y=adlib_y,
        z=adlib_z,
        mode='markers',
        marker=Marker(
            color='rgb(10,245,87)',
            size=12,
            symbol='circle',
            line=Line(
                color='rgb(0,0,0)',
                width=12
            )
        ),
        line=Line(
            color='rgb(10,245,87)',
            width=8
        ),
        name='Ad-lib'
    )

    opt_x, opt_y, opt_z = zip(*(sim.get_optimal_schedule()))

    trace3 = Scatter3d(
        x=opt_x,
        y=opt_y,
        z=opt_z,
        mode='markers',
        marker=Marker(
            color='rgb(245, 10, 10)',
            size=12,
            symbol='circle',
            line=Line(
                color='rgb(0,0,0)',
                width=12
            )
        ),
        line=Line(
            color='rgb(245, 10, 10)',
            width=8
        ),
        name='Optimal'
    )

    # Package the trace dictionary into a data object
    data = Data([trace1, trace2, trace3])

    # Dictionary of style options for all axes
    axis = dict(
        showbackground=True, # (!) show axis background
        backgroundcolor="rgb(204, 204, 204)", # set background color to grey
        gridcolor="rgb(255, 255, 255)",       # set grid line color
        zerolinecolor="rgb(255, 255, 255)",   # set zero grid line color
    )

    # Make a layout object
    layout = Layout(
        title='Time vs. Size vs. Rate', # set plot title
        showlegend=False,
        scene=Scene(  # (!) axes are part of a 'scene' in 3d plots
            xaxis=XAxis(title='time (days)'), # set x-axis style
            yaxis=YAxis(title='size (kg)'), # set y-axis style
            zaxis=ZAxis(title='rate (kg/day)'),  # set z-axis style,
        ),
        width=1200,
        height=900
    )

    # Make a figure object
    fig = Figure(data=data, layout=layout)

    plot_url = py.plot(fig, auto_open=False, filename='Simulation')
    return plot_url

if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)

