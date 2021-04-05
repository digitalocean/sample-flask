import stripe
import os

from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

print(stripe.Plan.list(limit=1))

app = Flask(__name__, static_folder='./client', static_url_path='', template_folder='./client')

@app.route('/')
def index():
    return render_template('index.html')

app.run(port=4242)

