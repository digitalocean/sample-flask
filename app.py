from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='frontend-dist', static_url_path='')

@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'index.html')

# This route is needed for the default path for all other routes not defined above
@app.route('/<path:path>')
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=True)
