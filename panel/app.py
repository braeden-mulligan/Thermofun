from flask import Flask, request, render_template, jsonify, Response, make_response

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def settings():
    return make_response(open('templates/index.html').read())

@app.route('/settings/<setting_name>/', methods=['GET'])
def get_setting(setting_name):
    settings = read_settings_file()
    if setting_name in settings:
        response = jsonify(
            setting_name=setting_name,
            setting_value=settings[setting_name])
    else:
        response = jsonify(message="Settings not found!")
        response.status_code = 404
    return response


@app.route('/settings/<setting_name>/', methods=['POST'])
def set_setting(setting_name):
    pass

def read_settings_file():
    settings = {}
    try:
        with open('../settings/settings.yml', 'r') as f:
            lines = f.readlines()
            for line in lines:
                try:
                    key, value = line.split(':')
                except ValueError:
                    continue
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
