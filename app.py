import os
from flask import Flask
from flask import render_template
import translations, translators, magazines, issues


app = Flask(__name__)
app.config['SECRET_KEY'] = 'xxxxxxxxxxxxxxxxx'

    
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

with app.app_context():
    app.register_blueprint(translations.bp)
    app.register_blueprint(translators.bp)
    app.register_blueprint(magazines.bp)
    app.register_blueprint(issues.bp)
