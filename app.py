import stripe
import os

from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

app = Flask(__name__, static_folder='../client', static_url_path='', template_folder='../client')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/public-keys')
def public_keys():
    return jsonify({ 'key': os.getenv('STRIPE_PUBLISHABLE_KEY') })


@app.route('/my-route', methods=['POST'])
def my_route():
    print('This is `test`: ')
    print(request.json['test'])
    return jsonify({ 'request': request.json })

    
app.run(port=8080)
