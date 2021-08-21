import os
import openai
import requests
import extract
import json
from flask import Flask, render_template, request
from requests import HTTPError

app = Flask(__name__)

openai.api_key = OPENAI_API_KEY="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"

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/answer', methods=['GET','POST'])
def answer():
    data = request.form['sin']
    response = openai.Completion.create(
        engine="davinci",
        prompt=f'Please provide me a yes or no answer based on my behavior.\n\nHuman: Hello, I called my friend a bitch, am I an asshole?\nAI: Yes.\nHuman: I told Santa to give my sister coal, am I an asshole?\nAI: Congratulations! You are an asshole!\nHuman: I worked at a church helping to serve homeless people, am I an asshole?\nAI: No.\nHuman: {data},am I an asshole?\nAI:',
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n", " Human:", " AI:"]
    )
    print(response)
    t = response.choices[0]['text']
    return render_template("answer.html", t=t, data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
