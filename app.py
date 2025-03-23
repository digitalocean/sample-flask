from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/tempate-creator")
def tempate-creator():
    return render_template("gen.html")
