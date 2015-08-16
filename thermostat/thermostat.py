#!/usr/bin/env python
# Thermostat controller

def clearPins():
	try:
		gpioStop = open("/sys/class/gpio/unexport/", 'w')
		gpioStop.write("17")
		gpioStop.write("27")
		gpioStop.close()
		return 0
	except:
		return 1

def initPins():
	try:
		gpioInit = open("/sys/class/gpio/export", 'w')
		gpioInit.write("17")
		gpioInit.write("27")
		gpioInit.close()

		gpioType = open("/sys/class/gpio/gpio17/direction", 'w')
		gpioType.write("out")
		gpioType.close()
		gpioType = open("/sys/class/gpio/gpio27/direction", 'w')
		gpioType.write("out")
		gpioType.close()
		return 0
	except:
		return 1

def switch(pin, state):
	try:
		gpio = open("/sys/class/gpio/gpio"+str(pin)+"/value", 'w')
		gpio.write("{}".format(state))
		return 0
	except:
		gpio.write("{}".format(0))
		return 1

def main():
	# switch(12, 22)

main()


