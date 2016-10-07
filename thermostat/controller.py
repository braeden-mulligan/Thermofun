# Thermostat controller

import time, sys, signal, threading, socket, requests
import RPi.GPIO as GPIO
import subroutine

if ('--verbose' in sys.argv) or ('-v' in sys.argv):
	DEBUG = True
else:
	DEBUG = False

# Track and control HVAC status.
ENABLE = True
ACTIVE = False
ACTIVE_LOCK = threading.Lock()
temperature = {'current':0.0, 'target':0.0}
temperature_lock = threading.Lock() 

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
FURNACE_FLAG = False
THERMOMETER_FLAG = False

def furnaceSafety(reason):
	global ACTIVE, ACTIVE_LOCK
	global FURNACE_FLAG 
	ACTIVE_LOCK.acquire(True)
	ACTIVE = switchOff()
	if FURNACE_FLAG:
		FURNACE_FLAG = False
	if reason == 'Furnace on too long!':
		time.sleep(900.0) # Grab lock and hold to force cooldown period.
	ACTIVE_LOCK.release()
	if DEBUG:
		print("Safety event, check logs.")
	subroutine.eventLog('* Safety switch triggered: ' + reason)
	return 0

# Globals for holding schedule data to make functions nicer.
agenda = []
schedules = []

def nextTimer():
# schedules[] lock not needed assuming only one timer thread can be active at a time.
	for s in schedules:
		s.cancel()
		schedules.remove(s)
	
	if not agenda:
		if DEBUG:
			print("No schedules found.\n")
	else:
		time_of_day = (time.localtime().tm_hour) * 3600
		time_of_day = time_of_day + ((time.localtime().tm_min) * 60)
		time_of_day = time_of_day + (time.localtime().tm_sec)

		delta_min = (24*60 + 1) * 60
		new_target = None
		for a in agenda:
			a_secs = (((a[0] / 100) * 60) + (a[0] % 100)) * 60
			time_gap = a_secs - time_of_day
			if time_gap < 1:
			# OK since schedules are unique and must have a time < 24:00.
				time_gap = time_gap + (24 * 3600)
			if time_gap < delta_min:
				delta_min = time_gap
				new_target = a[1]
		if DEBUG:
			print("Setting schedule timer for " + str(delta_min / 60)+"min " + str(delta_min % 60)+"sec.\n")
		schedules.append(threading.Timer(delta_min, changeTarget, kwargs={'target':new_target}))
		schedules[-1].daemon = True
		schedules[-1].start()
	return 0
	
def changeTarget(target):
	temperature_lock.acquire(True)
	if target:
		temperature['target'] = target
		dest = 'http://'+HOST_S+':'+str(PORT_S)+'/thermostat/target_change'
		payload = {'controller_data':temperature['target']}
		for i in range(4):
			try:
				requests.post(dest, data=payload)
			except:
				time.sleep(5)
			else:
				break
		else:
		# Not a catastrophic failure, just log it.
			subroutine.eventLog("Could not POST temperature data")
			if DEBUG:
				print("Network event, check logs.")
		if DEBUG:
			print("Temperature set to " + str(temperature['target']) + " as scheduled.")
	temperature_lock.release()
	if DEBUG:
		print("Schedule timer being recalculated...")
	nextTimer()
	return 0
	
	
def exitHandler(signum, frame):
	global ACTIVE, ACTIVE_LOCK
	if (ACTIVE):	
		ACTIVE = switchOff()
	GPIO.cleanup()
	if DEBUG:
		print("Exited gracefully.")
	sys.exit()


def main():
	global ENABLE, ACTIVE, ACTIVE_LOCK
	global HOST, PORT
	global safety_threads, FURNACE_FLAG, THERMOMETER_FLAG
	global agenda

	signal.signal(signal.SIGTERM, exitHandler)
	signal.signal(signal.SIGINT, exitHandler)
	
# Initial read of HVAC settings and status.
	for i in range(4):
		try:
			temp_re = requests.get('http://'+HOST_S+':'+str(PORT_S)+'/thermostat/target_change')
		except:
			time.sleep(5)
		else:
			break
	else:
		if DEBUG:
			print("Failed to GET initial target temperature.")
		exitHandler(None, None)
	temperature_lock.acquire(True)
	temperature['target'] = float(temp_re.text)
	threshold_high = temperature['target'] + 0.125
	threshold_low = temperature['target'] - 0.250
	temperature_lock.release()
	agenda = subroutine.getSchedules(DEBUG)
	nextTimer()

# Start socket to listen for settings changes from web app.
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.bind((HOST, PORT))
	except socket.error:
		if DEBUG:
			print("Socket bind failed.")
		exitHandler(None, None)

	soc.listen(1)
	soc.setblocking(1)

	message = {}
	message_lock = threading.Lock()
	arg_dict = {'soc':soc, 'msg':message, 'lck':message_lock, 'dbg':DEBUG}
	patience = threading.Thread(target=subroutine.getNotification, kwargs=arg_dict)
	patience.daemon = True # Otherwise cannot sigterm properly.
	patience.start()

	if DEBUG:
		print("Initialization success.")

# Keep track of ACTIVE threads.
	furnace_index = 0
	thermometer_index = 0

	interval = 28.0
# Start monitoring the system.
	while True:

		if ACTIVE:
			interval = 7.0
		else:
			interval = 49.0

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
	# query for, or have socket change ENABLE
			continue

	#	if DEBUG:
		#	temp_re = requests.get('http://'+HOST_S+':'+str(PORT_S)+'/thermostat/target_change')
		#	temperature['target'] = float(temp_re.text)
		#	print("Target acquired: " + str(temperature['target']))
	# Check for notification of changes to HVAC settings.
		target_change = None
		message_lock.acquire(True)
		if message: 
			target_change = float(message['target'])
			if DEBUG:
				print("Target acquired: " + str(target_change) + u"\u00B0C")
			message.clear()
		# Recalculate next schedule in case of changes.
			agenda = subroutine.getSchedules(DEBUG)
			nextTimer()
		message_lock.release()
		
		temperature_lock.acquire(True)
		if target_change:
			temperature['target'] = target_change
		threshold_high = temperature['target'] + 0.125
		threshold_low = temperature['target'] - 0.250
		temperature_lock.release()

		if DEBUG:
			print("Verifying temperature reading...")
	# Poll and verify thermometer reading.
	# Provide temporary-only power to thermometer to avoid heating it above ambient.
		GPIO.output(27, 1)
		time.sleep(1.125)
		temperature['current'] = subroutine.getTemperature(DEBUG)
		GPIO.output(27, 0)
		ACTIVE_LOCK.acquire(True)
		if temperature['current']:
			if DEBUG:
				print("Read OK. " + str(temperature['current']) + u"\u00B0C")
			if THERMOMETER_FLAG:
				THERMOMETER_FLAG = False
				safety_threads[thermometer_index].cancel()
			ACTIVE_LOCK.release()
		else:
			interval = 7.0
			if DEBUG:
				print("Could not poll temperature, trying again in "+ str(interval) + "s.")
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

		dest = 'http://'+HOST_S+':'+str(PORT_S)+'/thermostat/current_temperature'
		payload = {'controller_data':temperature['current']}
		for i in range(3):
			try:
				requests.post(dest, data=payload)
			except:
				time.sleep(3)
			else:
				break
		else:
			subroutine.eventLog("Could not POST temperature data")
			if DEBUG:
				print("Network event, check logs.")

		ACTIVE_LOCK.acquire(True)
		if (temperature['current'] < threshold_low):
			if ( not ACTIVE ):
				ACTIVE = switchOn()
				if not FURNACE_FLAG:
					FURNACE_FLAG = True
					safety_threads.append(threading.Timer(900.0, furnaceSafety, kwargs={'reason':'Furnace on too long!'}))
					furnace_index = len(safety_threads) - 1
					safety_threads[-1].daemon = True
					safety_threads[-1].start()
		if (temperature['current'] > threshold_high):
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
