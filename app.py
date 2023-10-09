from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/")
def contact():
    return render_template("contact.html")

@app.route("/")
def gift():
    return render_template("gift.html")

@app.route("/")
def news():
    return render_template("news.html")

@app.route("/")
def photos():
    return render_template("photos.html")

@app.route("/")
def trade():
    return render_template("trade.html")

@app.route("/")
def videos():
    return render_template("videos.html")




