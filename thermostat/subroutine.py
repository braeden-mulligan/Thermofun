import time, os, sys

THERMOMETER_URI = '/sys/bus/w1/devices/28-0000054b97a5/w1_slave'

def eventLog(message):
	entry = message + ": " + time.strftime("%Y-%m-%d, %H:%M:%S") + "\n"
	with open('controller_events.log', 'a') as f:
		f.write(entry)
	return 0

# Use sysfs to read thermometer.
def getTemperature(dbg):
	temperature = False
	try:
		with open(THERMOMETER_URI, 'r') as poll:
			measure = poll.readline()
			if measure.split()[11] == "YES":
				measure = poll.readline()
				temperature = (float(measure.split("t=")[1])) / 1000
			if temperature > 60:
			# Thermometer gave an error value.
				eventLog("Thermometer malfunction")
				temperature = False
	except IOError as err_msg:
		if dbg:
			eventLog(str(err_msg))
	return temperature

# For loading thermal profile settings:
from flask_sqlalchemy import SQLAlchemy
# Share db with flask app.
sys.path.append(os.path.dirname(os.getcwd()))
from control_panel import db, models
# Maybe not the best way to do this.
def getSchedules(dgb):
	profile_active = models.Profile.query.filter_by(active=True).first()
	schedules = profile_active.schedules.all()
	times = {}
	for s in schedules:
		times[s.time] = s.temperature
	return times

# Listen for changes to settings.
# TODO:
	# Error handling
def getNotification(soc, msg, lck, dbg):
	while 1:
		conn, addr = soc.accept()
		if dbg:
			print("Connected to " + str(addr[0]) + ":" + str(addr[1]))
		data = conn.recv(256)
		clean = data.strip()
		settings = clean.split(' ')
		lck.acquire(True)
		msg[settings[0]] = settings[1]
		msg[settings[2]] = settings[3]
		lck.release()
		conn.close()
	return 0
