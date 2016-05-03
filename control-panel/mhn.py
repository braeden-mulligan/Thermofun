#TODO: Implement schedule creation.

import sqlite3
from flask import Flask, render_template, request, url_for, g

app = Flask(__name__)

# Database functions ---
DATABASE = 'db/mhn.db'
def db_connect():
	return sqlite3.connect(DATABASE)

# Get a row from "settings" table.
def select_settings(name):
# Settings order: id, name, temp_status, temp_target, temp_max, enable
	setlist = [1,1,1,1,1,0]
	g.db = db_connect()
	curs = g.db.cursor()
	curs.execute('select * from settings where name=?', (name,))
	row = curs.fetchall()
	for i in range(0,5):
		setlist[i] = row[0][i]
# Debugging.
	print("DATABASE RETURN: " + str(setlist))
	g.db.close()
	return setlist

# Update a "settings" row in DB.
# Should be passed a six-element list of "settings" values.
# TODO: Generalize to all settings
def update_settings(setlist):
		g.db = db_connect()
		curs = g.db.cursor()
		name = setlist[1]
		val = setlist[3]
		curs.execute("UPDATE settings SET temp_target=? WHERE name=?", (val, name))
		g.db.commit()
# Debugging.
		print("DATABASE UPDATE: " + str(setlist))
		g.db.close()
# TODO: Return errors/successes properly?
		return 0
# --- 

# Webpage rendering ---
@app.route('/', methods=['GET'])
def index():
	t = "Homepage"
	p = ["Welcome to the Mulligan Home Network."]
	return render_template("index.html", title=t, paragraph=p[0])

@app.route('/about', methods=['GET'])
def about_page():
	t = "About"
	p = ["This website contains automation features for the house.", "Currently working features: "]
	pT = "about"
	return render_template("index.html", title=t, paragraph=p[0]+" "+p[1], pageType=pT)

@app.route('/thermostat/', methods=['GET', 'POST']) 
def thermostat_page():
	t = "Thermostat"
	p = ["Thermostat module control panel", "Current temperature: ", "Target temperature: "]
	pT = "thermostat"
	
	if request.method == 'GET':
#TODO: Report temp_max, enable.
#TODO: JS update temp_status with ajax in/decrementing.
		setlist = select_settings("Default")
		tstat = str(setlist[2])
		ttarg = str(setlist[3])

	if request.method == 'POST':
#TODO: Implement update temp_max, enable; allow variable row name
#TODO: Add confirmation flash
		val = float(request.form['temp-display'])
		name = "Default"
		setlist = select_settings(name)
		setlist[3] = val
		update_settings(setlist)
		
		tstat = str(setlist[2])
		ttarg = str(setlist[3])

#TODO: Make dict for render_template?
	return render_template('index.html', title=t, p0=p[0], p1=tstat, p2=ttarg, pageType=pT)
# ---

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
