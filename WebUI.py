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
		start_day = int(request.form['Start day'])
		end_day = int(request.form['End day'])
		m.main(start_day, end_day)
		return render_template("index.html")

if __name__ == '__main__':
    app.run(port=5001)

