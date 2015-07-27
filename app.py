from flask import Flask, request, redirect, url_for, session
app = Flask(__name__)

@app.route('/settings')
def display():
    if 'max_temp' in session:
        return session['max_temp']
    else:
        return 'No data'

@app.route('/', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        session['max_temp'] = request.form['max_temp']
        return redirect(url_for('settings'))
    return '''
        <form action="" method="post">
            <p><input type=text name=max_temp>
            <p><input type=submit value=Submit>
        </form>
    '''

if __name__ == '__main__':
    # set the secret key.  keep this really secret:
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host='0.0.0.0', debug=True)
