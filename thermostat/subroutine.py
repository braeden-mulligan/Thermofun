# Helper functions for controller

import time, os, sys, threading, socket

THERMOMETER_URI = '/sys/bus/w1/devices/28-0000054b97a5/w1_slave'
LOGFILE = 'incidents.log'
# Change argument to 'w' to clear logs on startup.
with open(LOGFILE, 'a') as f:
	pass

def eventLog(message):
	try:
	# Limit file size.
		with open(LOGFILE, 'r+') as f:
			line_count = sum(1 for line in f)
			if line_count > 1023:
				f.seek(0)
				for i in range(line_count - 1023):
					f.readline()
				remainder = f.read()
				f.seek(0)
				f.write(remainder)
				f.truncate()
		entry = message + " @ " + time.strftime("%Y-%m-%d, %H:%M:%S") + "\n"
		with open(LOGFILE, 'a+') as f:
			f.write(entry)
	except EnvironmentError:
		return 1
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
				if dbg:
					print("Thermometer error value " + str(temperature) + " reported.")
				temperature = None
	except EnvironmentError as e:
		if dbg:
			print(str(e))
	except Exception as e:
		if dbg:
			print("Thermometer event, check logs.")
		eventLog(str(e))
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
	timetable = []
	for i in range(3):
		try:
			profile_active = models.Profile.query.filter_by(active=True).first()
			schedules = profile_active.schedules.all()
	#	except SQLAlchemy.SQLAlchemyError as e:
	#		time.sleep(3)
		except Exception as e:
			time.sleep(3)
		else:
			for s in schedules:
				timetable.append((s.time, s.temperature))
			break
	else:
		eventLog(str(e))
		if dbg:
			print("Database event, check logs.")
	return timetable

# Listen for changes to settings.
# msg should be an empty dictionary
def getNotification(soc, msg, lck, dbg):
	while 1:
		conn, addr = soc.accept()
		if dbg:
			print("Connected to " + str(addr[0]) + ":" + str(addr[1]))
		try:
			data = conn.recv(256)
		except Exception as e:
			if dbg:
				print("Network event, check logs.")
			eventLog(str(e))
		else:
			clean = data.strip()
			settings = clean.split(' ')
			lck.acquire(True)
			msg[settings[0]] = settings[1]
			lck.release()
			if dbg:
				print("Successfully received data.\n")
		conn.shutdown(socket.SHUT_RD)
		conn.close()
	return 0
