from flask import Flask, request, url_for, render_template

app = Flask(__name__)

@app.route('/edit', methods=['GET'])
def edit_settings():
    return render_template('edit.html')

@app.route('/', methods=['GET', 'POST'])
def display_settings():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
