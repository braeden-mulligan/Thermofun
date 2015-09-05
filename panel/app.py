from flask import Flask, request, render_template, jsonify, Response, make_response

app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET', 'POST'])
def settings():
    return make_response(open('templates/index.html').read())

@app.route('/api/settings/', methods=['GET'])
def get_setting():
	settings = read_settings_file()
	response = jsonify(settings)
	return response, 200

@app.route('/api/settings/', methods=['POST'])
def set_setting():
    settings = request.get_json()
    if not 'enabled' in settings or not 'target_temp' in settings:
        abort(400)
    success = write_settings_file(settings)
    return jsonify(test="Test")

def read_settings_file():
    settings = {}
    try:
        with open('../settings/settings.yml', 'r') as f:
            lines = f.readlines()
            for line in lines:
				key, value = line.split(':')
				value = value.strip().strip('\n')
				settings[key] = value
        return settings
    except IOError:
        return None

def write_settings_file(settings):
    settings_string = ''
    for key, value in settings.iteritems():
        settings_string += '{k}: {v}\n'.format(k=key, v=value)
    try:
        with open('../settings/settings.yml', 'w') as f:
            f.write(settings_string)
        return True
    except IOError:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
