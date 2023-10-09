from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/gift")
def gift():
    return render_template("gift.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/photos")
def photos():
    return render_template("photos.html")

@app.route("/trade")
def trade():
    return render_template("trade.html")

@app.route("/videos")
def videos():
    return render_template("videos.html")




