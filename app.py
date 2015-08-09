from flask import Flask, request, redirect, url_for, session, render_template
app = Flask(__name__)

@app.route('/edit', methods=['GET', 'POST'])
def edit_settings():
    return render_template('edit.html')

@app.route('/', methods=['GET', 'POST'])
def display_settings():
    return render_template('main.html')

if __name__ == '__main__':
    # set the secret key.  keep this really secret:
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host='0.0.0.0', debug=True)
