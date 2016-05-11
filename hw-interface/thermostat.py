#!/usr/bin/env python
# Thermostat controller

# NOTE: Currently lacking error handling !!
# TODO: Support HVAC schedules

import time, sys, signal
import RPi.GPIO as GPIO
# import requests # Not sure why this was here
import sqlite3


def main():

	active = 0
	temp_current = 25
	enable = 1
	safecycle = 0
	errorcycle = 0

	def exitHandler( signum, frame ):
		if (active):		
			switchOff()
		GPIO.cleanup()
		sys.exit()

	signal.signal(signal.SIGTERM, exitHandler)
	signal.signal(signal.SIGINT, exitHandler)

# Pin control ---
	GPIO.setmode(GPIO.BCM) # Pin numbering scheme.
	GPIO.setup(17, GPIO.OUT)
	GPIO.setup(27, GPIO.OUT)

	def switchOn():
		GPIO.output(17, 1)
# Debugging.
		print("Switched ON at " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		return 1

	def switchOff():
		global safecycle
		GPIO.output(17, 0)
		safecycle = 0
# Debugging.
		print("Switched OFF at " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		return 0
# ---

# Database ---
	DATABASE = '/home/pi/Documents/Software/Thermofun/control-panel/db/mhn.db'
	def dbConnect():
		return sqlite3.connect(DATABASE)

# TODO: Support multiple settings profiles.
	def selectSettings(name):
		setlist = [1, None, 0, 0, 0, 0]
		db = dbConnect()
		curs = db.cursor()
		curs.execute('SELECT * FROM settings WHERE name=?', (name,))
		row = curs.fetchall()
		for i in range(6):
			setlist[i] = row[0][i]
		db.close()
		return setlist

# Should be passed a six-element list "settings" and "current temperature" float
	def updateSettings(setlist, val):
		db = dbConnect()
		curs = db.cursor()
		name = setlist[1]
		curs.execute('UPDATE settings SET temp_status=? WHERE name=?', (val, name))
		db.commit()
		db.close()
		return 0
# ---

# Settings order: [id, name, temp_status, temp_target, temp_max, enable]
	settingslist = [1, None, 0, 0, 0, 0]
	threshold_high = settingslist[3] + 0.250
	threshold_low = settingslist[3] - 0.375

#	def dataLog():

# Debugging.
	print("Initializations complete.")
	while 1:
		settingslist = selectSettings('Default')
		threshold_high = settingslist[3] + 0.250
		threshold_low = settingslist[3] - 0.375

		GPIO.output(27, 1)
		time.sleep(0.200)
		try:
			with open('/sys/bus/w1/devices/28-0000054b97a5/w1_slave', 'r') as poll:
				measure = poll.readline()
				if(measure.split()[11] == "YES"):
					measure = poll.readline()
					temp_current = ((float)(measure.split("t=")[1]))/1000
# If thermometer data gives an error value.
				if (temp_current > 60):
					temp_current = settingslist[2]
				
			errorcycle = 0
		except IOError as emsg:
			print("Error: %s" % str(emsg))
			errorcycle += 1
# Debugging
			print("Error count: %s" % str(errorcycle))
# If temperature cant be read for over two minutes, switch system off
			if ( errorcycle > 23 ):
				if (active):
					active = switchOff()
					exitHandler(0, 0)
		except:
			print("Error: Other")
			if (active):
				active = switchOff()
				exitHandler(0, 0)
		GPIO.output(27, 0)

		updateSettings(settingslist, temp_current)

# Decide if furnace should switch on ---
		if ( (temp_current > settingslist[4]) or (not settingslist[5]) ):
			if (active):
				active = switchOff()
				safecycle = 0
		else:
			if ( (temp_current < threshold_low) ):
				if ( not active ):
					active = switchOn()
			if ( (temp_current > threshold_high) ):
				if ( active ):
					active = switchOff()
					safecycle = 0
# ---
		time.sleep(4.8)

# Temporary safety precaution ---
		if( active ):
			safecycle += 1
# Switch off after 25 minutes of continuous activity.
			if ( safecycle >= 300 ):
				active = switchOff()
				safecycle = 0
				print("* Furnace overtime! Shutting off for 10 minutes.")
				with open('safety_log', 'w+') as log:
					log.write("Activity overtime triggered.")
				time.sleep(600)
# ---

if __name__ == "__main__":
	main()
