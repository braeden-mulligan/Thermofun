#!/usr/bin/env python
# Thermostat controller

import time
#import RPi.GPIO as GPIO

def switchOn():
#	GPIO.output(27, 1)
	time.sleep(0.265)
#	GPIO.output(27, 0)

def switchOff():
#	GPIO.output(17, 1)
	time.sleep(0.265)
#	GPIO.output(17, 0)

if __name__ == "__main__":
#	GPIO.setmode(GPIO.BCM)
#	GPIO.setup(27, GPIO.OUT)
#	GPIO.setup(17, GPIO.OUT)

	enable = 0
	cutoff = 25.0
	target = 21.0
	thresh_high = target + 1.0
	thresh_low = target - 1.0

	thermo = 20.0
	active = 0

	while True:
		with open("/sys/bus/w1/devices/28-0000054bcb79/w1_slave", 'r') as poll:
			measure = poll.readline()
			if measure.split()[11] == "YES":
				measure = poll.readline()
				thermo = ((float)(measure.split("t=")[1]))/1000

		with open("../settings/settings.yml", 'r') as settings:
			for line in settings:
				if line.split(": ")[0] == "enabled":
					enable = line.split(": ")[1]
				elif line.split(": ")[0] == "max_temp":
					cutoff = line.split(": ")[1]
				elif line.split(": ")[0] == "target_temp":
					target = line.split(": ")[1]
		thresh_high = target + 1.0
		thresh_low = target - 1.0

		if (thermo > cutoff) or (enable == 0) :
			if active == 1:
				switchOff()
				active = 0
			time.sleep(30)
		else:
			if (thermo < thresh_low) and (active == 0):
				switchOn()
				active = 1
			elif (thermo > thresh_high) and (active == 1):
				switchOff()
				active = 0
			
			time.sleep(30)

	# Only useful if user can set a parameter to exit the loop
#	GPIO.cleanup()
