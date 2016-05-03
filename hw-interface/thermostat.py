#!/usr/bin/env python
# Thermostat controller

import time
import RPi.GPIO as GPIO
import requests
import sys
import signal


def main():

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(27, GPIO.OUT)
	GPIO.setup(17, GPIO.OUT)

	active = 0

	def exitHandler( signum, frame ):
		if (active):		
			switchOff()
		GPIO.cleanup()
		sys.exit()

	def switchOn():
		GPIO.output(27, 1)
		time.sleep(0.275)
		GPIO.output(27, 0)
		return 1

	def switchOff():
		GPIO.output(17, 1)
		time.sleep(0.215)
		GPIO.output(17, 0)
		return 0

#	def exitLog():
#	def dataLog():
	
	enable = 0
	cutoff = 25.000
	target = 20.000
	thresh_high = target + 0.250
	thresh_low = target - 0.375
	thermo = 20.0
#	scheds = []

#TODO: Avoid unecessary reads, mod out a count
	cycle = 0
	
	signal.signal( signal.SIGTERM, exitHandler )
	signal.signal( signal.SIGINT, exitHandler )

	while True:
		with open("/sys/bus/w1/devices/28-0000054bcb79/w1_slave", 'r') as poll:
			measure = poll.readline()
			if(measure.split()[11] == "YES"):
				measure = poll.readline()
				thermo = ((float)(measure.split("t=")[1]))/1000

		#TODO: if <not schedules active>
		with open("../settings/settings.yml", 'r') as settings:
			for line in settings:
				if line.split(": ")[0] == "enabled":
					enable = (line.split(": ")[1]) #TODO: Check API
				elif line.split (": ")[0] == "max_temp":
					cutoff = (float)(line.split(": ")[1])
				elif line.split(": ")[0] == "target_temp":
					target = (float)(line.split(": ")[1])
		thresh_high = target + 0.250
		thresh_low = target - 0.375

# TODO: remove after debugging
		enable = 1;

		if ((thermo > cutoff) or (not enable)):
			if (active):
				active = switchOff()
		else:
			if ((thermo < thresh_low) and (not active)):
				active = switchOn()
			if ((thermo > thresh_high) and (active)):
				active = switchOff()

		time.sleep(5)


if __name__ == "__main__":
	main()
