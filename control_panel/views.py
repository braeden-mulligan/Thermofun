from flask import render_template, url_for, request, redirect
from control_panel import app, db, models, temp_target, temp_current
import time

def eventLog(message):
	entry = message + " " + time.strftime("%Y-%m-%d, %H:%M:%S")
	with open("events.log", "a") as f:
		f.write(entry)


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
	return render_template('index.html', title="Home")


@app.route('/thermostat', methods=['GET', 'POST'])
def thermostat():
	global temp_current
	global temp_target
	print(str(temp_target) + " from GET")
	content = {'title':"Thermostat"}

	profiles = models.Profile.query.all()
	profile_active = []
	for p in profiles:
		if p.active:
			profile_active.append(p)
# Fall back to default if errors.
	if len(profile_active) > 1:
		profile_active[0] = models.Profile.query.filter_by(name='DEFAULT').first()
		if DEBUG:
			eventLog("Too many active profiles")
	if len(profile_active) < 1:
		profile_active[0] = models.Profile.query.filter_by(name='DEFAULT').first()
		if DEBUG:
			eventLog("No active profiles")

# Choose profile.
# TODO:
	# socket notification
	# change method of submission?
	# data validation
	if request.method == 'POST':
		if 'profile_selection' in request.form:
			selection = request.form['profile_selection']
			if selection == 'profile_delete':
				marked = profile_active[0]
				if marked.name == 'DEFAULT':
					eventLog("Attempted deletion of DEFAULT profile")
				else:
					default = models.Profile.query.filter_by(name='DEFAULT').first()
# TODO:
	# handle errors
					default.active = True
					profile_active[0] = default
					profiles.remove(marked)
					db.session.delete(marked)
					db.session.commit()
			elif selection != 'profile_add':
				new_active = models.Profile.query.filter_by(name=request.form['profile_selection']).first()
				profile_active[0].active = False
				new_active.active = True
				db.session.commit()
				profile_active[0] = new_active
				temp_target = new_active.temperature
# Bring active profile to top for display.
# TODO:?
	# sort lexicographically.
	profiles.insert(0, profiles.pop(profiles.index(profile_active[0])))
	content['profiles'] = profiles

# Modify profile's existing schedules.
	if request.method == 'POST':
# TODO:
	# data validation
	# socket notification
		if 'schedule_modify' in request.form:
			shedule_mod = models.Schedule.query.filter_by(id=request.form['schedule_modify']).delete()
			db.session.commit()
		if 'schedule_target' in request.form:
			new_temperature = round(float(request.form['schedule_target']), 1)
			hr = request.form['schedule_hour']
			mi = request.form['schedule_minute']
			if (int(hr) >= 0) and (int(hr) <= 23):
				if (int(mi) >= 0) and (int(mi) <= 59):
					new_time = (int(hr) * 100) + int(mi)
					if not new_time:
						new_time = 1
					new_schedule = models.Schedule(new_temperature, new_time)
					new_schedule.profile = profile_active[0]
					db.session.add(new_schedule)
					db.session.commit()
	content['schedules'] = profile_active[0].schedules.all()
	content['temp_current'] = round(temp_current, 1)
	content['temp_target'] = round(temp_target, 1)

	return render_template('thermostat.html', **content)
# END def thermostat()

# Will also be used by hardware controller.
@app.route('/thermostat/target_change', methods=['POST'])
def target_change():
	global temp_target
	if 'target_modify' in request.form:
		temp_target = round(float(request.form['target_modify']), 1)
	return redirect(url_for('thermostat'))


@app.route('/thermostat/profile_create', methods=['GET', 'POST'])
def profile_create():
	if request.method == 'GET':
		content = {'title':"Thermal Profile Config"}
		return render_template('profile_create.html', **content)
	else:
# TODO:
	# Name 'profile_add' is reserved.
	# General input validation.
	# socket notification.
		new_p_name = request.form['new_profile_name']
		new_p_temperature = round(float(request.form['new_profile_temperature']), 1)
		new_profile = models.Profile(new_p_name, new_p_temperature)
		db.session.add(new_profile)
		db.session.commit()
		count = 0;
		while ('new_schedule_target' + str(count)) in request.form:
			init_temperature = round(float(request.form['new_schedule_target' + str(count)]), 1)
			hr = request.form['new_schedule_hour' + str(count)]
			mi = request.form['new_schedule_minute' + str(count)]
			if (int(hr) >= 0) and (int(hr) <= 23):
				if (int(mi) >= 0) and (int(mi) <= 59):
					init_time = (int(hr) * 100) + int(mi)
					if not init_time:
						init_time = 1
					init_schedule = models.Schedule(init_temperature, init_time)
					init_schedule.profile = new_profile
					db.session.add(init_schedule)
					db.session.commit()
			count += 1
		
		return redirect(url_for('thermostat'))
# END def profile_create()

@app.route('/sprinkler')
def sprinkler():
	return "Feature not yet available."
