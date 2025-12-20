import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# قراءة المتغيرات البيئية
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "openai_key_loaded": bool(OPENAI_API_KEY),
        "database_loaded": bool(DATABASE_URL)
    })
