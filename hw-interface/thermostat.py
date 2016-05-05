#!/usr/bin/env python
# Thermostat controller

# NOTE: Currently lacking error handling !!
# TODO: Support HVAC schedules

import time, sys, signal
import RPi.GPIO as GPIO
# import requests # Not sure why this was here
import sqlite3

def main():

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

	def switchOn():
		GPIO.output(17, 1)
# Debugging.
		print("Switched ON at " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
		return 1

	def switchOff():
		GPIO.output(17, 0)
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
	
	temp_current = 0
	enable = 1
	active = 0
	cycle = 0

#	def dataLog():

# Debugging.
	print("Initializations complete.")
	while 1:
		settingslist = selectSettings('Default')
		threshold_high = settingslist[3] + 0.250
		threshold_low = settingslist[3] - 0.375

		with open('/sys/bus/w1/devices/28-0000054bcb79/w1_slave', 'r') as poll:
			measure = poll.readline()
			if(measure.split()[11] == "YES"):
				measure = poll.readline()
				temp_current = ((float)(measure.split("t=")[1]))/1000

		updateSettings(settingslist, temp_current)

		if ( (temp_current > settingslist[4]) or (not settingslist[5]) ):
			if (active):
				active = switchOff()
		else:
			if ( (temp_current < threshold_low) ):
				if ( not active ):
					active = switchOn()
			if ( (temp_current > threshold_high) ):
				if ( active ):
					active = switchOff()

		time.sleep(5)

# Temporary safety precaution ---
		if( active ):
			cycle += 1
# Switch off after 25 minutes of continuous activity.
			if ( cycle >= 300 ):
				active = switchOff()
				cycle = 0
				print("* Furnace overtime! Shutting off for 30 minutes.")
				time.sleep(1800)
# ---

if __name__ == "__main__":
	main()
