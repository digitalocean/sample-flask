from flask import Flask, render_template
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    now = datetime.datetime.utcnow()
    timeString = now.strftime("%a %b %d %I:%M:%S %Y")
    templateData = {
        'title' : 'HELLO!',
        'time': timeString
        }
    return render_template('index.html', **templateData)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')