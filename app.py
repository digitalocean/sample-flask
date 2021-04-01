import os

import stripe
import didkit
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
}

stripe_prices = {
    "subscription": os.environ["SUBSCRIPTION_PRICE_ID"],
}

stripe.api_key = stripe_keys["secret_key"]


@app.route("/")
def index():
    domain = request.url_root.split(
        "https://")[-1].split("http://")[-1].replace("/", "")
    return render_template("index.html", domain=domain)


@app.route("/success")
def success():
    # mail guy
    return 'Success'


@app.route("/cancelation")
def cancelation():
    return 'Canceled'


@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)


@app.route("/create-checkout-session")
def create_checkout_session():
    domain_url = "http://localhost:5000/"
    stripe.api_key = stripe_keys["secret_key"]
    subscription = stripe.Price.retrieve(stripe_prices["subscription"])

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - capture the payment later
        # [customer_email] - prefill the email input in the form
        # For full details see https://stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url +
            "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "name": subscription["nickname"],
                    "quantity": subscription["recurring"]["interval_count"],
                    "currency": subscription["currency"],
                    "amount": subscription["unit_amount"],
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403
