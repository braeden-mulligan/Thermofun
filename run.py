#!env/bin/python
from control_panel import app

# execute as processes:
# thermostat
# sprinkler
# web interface

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)
