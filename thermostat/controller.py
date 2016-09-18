# Thermostat controller
# TODO:
	# midnight timer
DEBUG = True

import time, sys, signal, threading, socket, requests
import RPi.GPIO as GPIO
import subroutine

ENABLE = True
INTERVAL = 30

# Socket config.
HOST = 'localhost'
PORT = 5001

def main():
	global ENABLE, INTERVAL
	global HOST, PORT

# Track HVAC status.
	active = False
	temp_current = 0.0
# TODO:
	# Re-engineer safety mechanisms
	# see switchOff()
	safecycle = 0
	errorcycle = 0

	def exitHandler(signum, frame):
		if (active):		
			switchOff()
		GPIO.cleanup()
		print("Exiting gracefully.")
		sys.exit()

	signal.signal(signal.SIGTERM, exitHandler)
	signal.signal(signal.SIGINT, exitHandler)

	GPIO.setmode(GPIO.BCM) # Pin numbering scheme.
	GPIO.setup(17, GPIO.OUT)
	GPIO.setup(27, GPIO.OUT)

	def switchOn():
		GPIO.output(17, 1)
		if DEBUG:
			print("Switched ON at " + time.strftime("%Y-%m-%d, %H:%M:%S.", time.localtime()))
		return 1

	def switchOff():
		global safecycle
		safecycle = 0
		GPIO.output(17, 0)
		if DEBUG:
			print("Switched OFF at " + time.strftime("%Y-%m-%d, %H:%M:%S.", time.localtime()))
		return 0

# Get current HVAC settings and status.
# TODO:
	# handle errors
	agenda = subroutine.getSchedules(DEBUG)
	temp_re = requests.get('http://'+HOST+':5000/thermostat/target_change')
	temp_target = (float(temp_re.text))

# Start socket to listen for settings changes from web app.
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.bind((HOST, PORT))
	except socket.error:
		print("Socket bind failed.")
		exitHandler(None, None)

	soc.listen(2)
	soc.setblocking(1)

	message = {} # Should be mutable
	message_lock = threading.Lock()

	arg_dict = {'soc':soc, 'msg':message, 'lck':message_lock, 'dbg':DEBUG}
	patience = threading.Thread(target=subroutine.getNotification, kwargs=arg_dict)
	patience.daemon = True # Otherwise cannot sigterm main.
	patience.start()	

	if DEBUG:
		print("Initialization success.")

	while True:

		GPIO.output(27, 1)
		time.sleep(0.200)
		temp_current = subroutine.getTemperature(DEBUG)
# TODO:
	# verify temp read succesful

		print(str(temp_current))
		time.sleep(30)
'''		
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

'''

if __name__ == '__main__':
	main()
