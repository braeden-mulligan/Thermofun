import time

def eventLog(message):
	entry = message + ": " + time.strftime("%Y-%m-%d, %H:%M:%S") + "\n"
	with open('events.log', 'a') as f:
		f.write(entry)
	return 0

# Tell hw controller to query for current settings.
def notifyHw():
	return 0
