from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about.html")
def index():
    return render_template("about.html")

@app.route("/contact.html")
def contact():
    return render_template("contact.html")

@app.route("/gift.html")
def gift():
    return render_template("gift.html")

@app.route("/news.html")
def news():
    return render_template("news.html")

@app.route("/photos.html")
def photos():
    return render_template("photos.html")

@app.route("/trade.html")
def trade():
    return render_template("trade.html")

@app.route("/videos.html")
def videos():
    return render_template("videos.html")




