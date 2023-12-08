# app.py
from flask import Flask
from flask import render_template, request

app = Flask(__name__)


@app.route("/")
def hello_world():
    print("Hello world")
    return render_template("index.html")


@app.route("/sample_form", methods=['GET', 'POST'])
def sample_form():
    print("Accessed sample_form")
    if request.method == 'POST':
        if request.form['submit'] == 'pdf':
            print("PDF form submitted")
            file = request.files['file']
            file_data = file.read()
        elif request.form['submit'] == 'stamp':
            print("Stamp form submitted")
            form_data = request.form.to_dict()
    return render_template("sample_form.html")


if __name__ == "__main__":
    app.run()
