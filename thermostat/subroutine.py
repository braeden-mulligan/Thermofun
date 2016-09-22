# Helper functions for controller

import time, os, sys, threading

THERMOMETER_URI = '/sys/bus/w1/devices/28-0000054b97a5/w1_slave'

def eventLog(message):
	entry = message + " @ " + time.strftime("%Y-%m-%d, %H:%M:%S") + "\n"
	with open('controller_events.log', 'a') as f:
		f.write(entry)
	return 0

# Use sysfs to read thermometer.
def getTemperature(dbg):
	temperature = None
	try:
		with open(THERMOMETER_URI, 'r') as poll:
			measure = poll.readline()
			if measure.split()[11] == "YES":
				measure = poll.readline()
				temperature = (float(measure.split("t=")[1])) / 1000
			if temperature > 80:
			# Thermometer gave an error value.
				temperature = None
				eventLog("Thermometer error value reported")
	except IOError as err_msg:
		dbg = False
		if dbg:
			eventLog(str(err_msg))
	return temperature

# For loading thermal profile settings:
from flask_sqlalchemy import SQLAlchemy
# Share db with flask app.
# TODO:
	# make absolute path
sys.path.append(os.path.dirname(os.getcwd()))
from control_panel import db, models
# Maybe not the best way to do this.
def getSchedules(dgb):
	profile_active = models.Profile.query.filter_by(active=True).first()
	schedules = profile_active.schedules.all()
	timetable = []
	for s in schedules:
		timetable.append((s.time, s.temperature))
	return timetable

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
		lck.release()
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()
	return 0
