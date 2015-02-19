import sqlite3
from flask import *
import Main as m

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

		start_day = int(request.form.get('Start day', 1, type=int))
		end_day = int(request.form.get('End day', 80, type=int))
		extend_days = int(request.form.get('Extend days', 0, type=int))
		price_per_kg = int(request.form.get('Price per kg', 2.89, type=float))
		food_cost = int(request.form.get('Food cost', 0.25, type=float))
		facility_cost = int(request.form.get('Facility cost', 0.35, type=float))
		r_value = int(request.form.get('R value', 0.075, type=float))

		m.main(start_day, end_day) #change this call to use all parameters
		return render_template("index.html")

if __name__ == '__main__':
    app.run(port=5001)

