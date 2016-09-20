# Thermostat controller
# TODO:
	# midnight timer
DEBUG = True

import time, sys, signal, threading, socket, requests
import RPi.GPIO as GPIO
import subroutine

# Control HVAC status.
ENABLE = True
ACTIVE = False
ACTIVE_LOCK = threading.Lock()

# Socket config.
HOST = 'localhost'
PORT = 5001

# Web server.
HOST_S = 'localhost'
PORT_S = 5000

GPIO.setmode(GPIO.BCM) # Pin numbering scheme.
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

def switchOn():
	GPIO.output(17, 1)
	if DEBUG:
		print("Switched ON at " + time.strftime("%Y-%m-%d, %H:%M:%S.", time.localtime()))
	return True

def switchOff():
	GPIO.output(17, 0)
	if DEBUG:
		print("Switched OFF at " + time.strftime("%Y-%m-%d, %H:%M:%S.", time.localtime()))
	return False

# Start shutoff countdown when thermometer can't be read for long periods.
# Or if furnace has been on for too long.
# Cancel once normal operations resume.
safety_threads = []
#TODO: cut inACTIVE threads from list
FURNACE_FLAG = False
THERMOMETER_FLAG = False

def furnaceSafety(reason):
	global ACTIVE, ACTIVE_LOCK
	global FURNACE_FLAG, FLAG_LOCK
	ACTIVE_LOCK.acquire(True)
	ACTIVE = switchOff()
	if FURNACE_FLAG:
		FURNACE_FLAG = False
	if reason == 'Furnace on too long!':
		time.sleep(900.0) # Grab lock and hold to force cooldown period.
	ACTIVE_LOCK.release()
	if DEBUG:
		subroutine.eventLog('* Safety switch triggered: ' + reason)
		print("Safety event, check logs.")
	return 0
	
def exitHandler(signum, frame):
	global ACTIVE, ACTIVE_LOCK
	ACTIVE_LOCK.acquire(True)
	if (ACTIVE):		
		ACTIVE = switchOff()
	ACTIVE_LOCK.release()
	GPIO.cleanup()
	print("Exiting gracefully.")
	sys.exit()


def main():
	global ENABLE, ACTIVE, ACTIVE_LOCK
	global HOST, PORT
	global safety_threads, FURNACE_FLAG, THERMOMETER_FLAG

	signal.signal(signal.SIGTERM, exitHandler)
	signal.signal(signal.SIGINT, exitHandler)
	
	temp_current = 0.0
# Initial read of HVAC settings and status.
# TODO: handle errors
	agenda = subroutine.getSchedules(DEBUG)
	temp_re = requests.get('http://'+HOST_S+':'+str(PORT_S)+'/thermostat/target_change')
	temp_target = (float(temp_re.text))
	threshold_high = temp_target - 0.250
	threshold_low = temp_target + 0.250

# Start socket to listen for settings changes from web app.
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.bind((HOST, PORT))
	except socket.error:
		print("Socket bind failed.")
		exitHandler(None, None)

	soc.listen(1)
	soc.setblocking(1)

	message = {} # Should be mutable
	message_lock = threading.Lock()
	arg_dict = {'soc':soc, 'msg':message, 'lck':message_lock, 'dbg':DEBUG}
	patience = threading.Thread(target=subroutine.getNotification, kwargs=arg_dict)
	patience.daemon = True # Otherwise cannot sigterm main.
	patience.start()

	if DEBUG:
		print("Initialization success.")

# Keep track of ACTIVE threads.
	furnace_index = 0
	thermometer_index = 0

	interval = 30.0
# Start monitoring the system.
	while True:

		if ACTIVE:
			interval = 7.0
		else:
			interval = 60.0

		if not ENABLE:
			if ACTIVE:
				ACTIVE_LOCK.acquire(True)
				ACTIVE = switchOff()
				if FURNACE_FLAG:
					FURNACE_FLAG = False
					safety_threads[furnace_index].cancel()
				ACTIVE_LOCK.release()
			time.sleep(interval)
#TODO: Will get stuck in infinite loop here
	# query for enable
			continue

	# Check for changes in HVAC settings.
		if DEBUG:
			temp_re = requests.get('http://'+HOST_S+':'+str(PORT_S)+'/thermostat/target_change')
			temp_target = float(temp_re.text)
			print("Target acquired: " + str(temp_target))
		message_lock.acquire(True)
		if message:
			temp_target = float(message['target'])
			message = None
# TODO:		get schedules
		message_lock.release()

		threshold_high = temp_target + 0.250
		threshold_low = temp_target - 0.250

	# Poll and verify thermometer reading.			
		GPIO.output(27, 1)
		time.sleep(0.200)
		temp_current = subroutine.getTemperature(DEBUG)
		GPIO.output(27, 0)
		if DEBUG:
			print("Verifying temperature reading...")
		if temp_current:
			if DEBUG:
				print("Read OK.")
			ACTIVE_LOCK.acquire(True)
			if THERMOMETER_FLAG:
				THERMOMETER_FLAG = False
				safety_threads[thermometer_index].cancel()
			ACTIVE_LOCK.release()
		else:
			interval = 7.0
			if DEBUG:
				print("Could not poll temperature, trying again in "+ str(interval) + "s.")
			ACTIVE_LOCK.acquire(True)
			if ACTIVE and (not THERMOMETER_FLAG):
				THERMOMETER_FLAG = True
			# Bad reads occur frequently, no need to kill furnace immediately.
				safety_threads.append(threading.Timer(120.0, furnaceSafety, kwargs={'reason':'Failed to get temperature for extended period'}))
				thermometer_index = len(safety_threads) - 1
				safety_threads[-1].daemon = True
				safety_threads[-1].start()
			ACTIVE_LOCK.release()
			time.sleep(interval)
		# Avoid switching furnace on until temperature can be properly read.
			continue 

# TODO:
	# error handling
		dest = 'http://'+HOST_S+':'+str(PORT_S)+'/thermostat/current_temperature'
		payload = {'controller_data':temp_current}
		temp_post = requests.post(dest, data=payload)

		ACTIVE_LOCK.acquire(True)
		if (temp_current < threshold_low):
			if ( not ACTIVE ):
				ACTIVE = switchOn()
				if not FURNACE_FLAG:
					FURNACE_FLAG = True
					safety_threads.append(threading.Timer(900.0, furnaceSafety, kwargs={'reason':'Furnace on too long!'}))
					furnace_index = len(safety_threads) - 1
					safety_threads[-1].daemon = True
					safety_threads[-1].start()
		if (temp_current > threshold_high):
			if ( ACTIVE ):
				ACTIVE = switchOff()
				if FURNACE_FLAG:
					FURNACE_FLAG = False
					safety_threads[furnace_index].cancel()
		ACTIVE_LOCK.release()

	# Clear dead threads if there are none running.
	# Not guarunteed to be 100% stable but should work in practice.
		any_alive = False
		for i in range(len(safety_threads)):
			if safety_threads[i].isAlive():
				any_alive = True
		if not any_alive:
			if DEBUG:
				print("Safety list cleared.")
			del safety_threads[:]
		else:
			if DEBUG:
				print("Safety list has live threads.")

		if DEBUG:
			if ACTIVE:
				print("Furnace working...")		
			else:
				print("Furnace inactive.")
			print("Sleeping for " + str(interval) +"s.\n")
		time.sleep(interval)
	# END loop


if __name__ == '__main__':
	main()
