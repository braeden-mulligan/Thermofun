import time, socket

HOST_C = 'localhost'
PORT_C = 5001

def eventLog(message):
	entry = message + ": " + time.strftime("%Y-%m-%d, %H:%M:%S") + "\n"
	with open('network_events.log', 'a') as f:
		f.write(entry)
	return 0

# Tell hw controller to query for current settings.
def notifyHw(temperature):
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.connect((HOST_C, PORT_C))
		data = "target " + str(temperature)
		soc.send(data)
	except socket.error:
		return 1
	soc.shutdown(socket.SHUT_WR)
	soc.close()
	return 0
