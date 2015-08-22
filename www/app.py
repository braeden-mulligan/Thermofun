from flask import Flask, request, url_for, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def settings():
    settings = read_settings_file()
    if request.method == 'POST':
        if 'enabled' in settings and 'enabled' not in request.form:
            settings['enabled'] = '0'
        for key, value in request.form.iteritems():
            if key == 'enabled':
                settings[key] = '1'
            else:
                settings[key] = request.form[key]
        write_settings_file(settings)
    return render_template('main.html', settings=settings)

@app.route('/status/', methods=['GET'])
def status():
    

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
