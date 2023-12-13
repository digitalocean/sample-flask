import time

from flask import Flask, send_from_directory, request
import cutsheet_module as cs

app = Flask(__name__, static_folder='frontend-dist', static_url_path='')


@app.route("/")
def index():
    return send_from_directory(app.static_folder, 'index.html')


# This route is needed for the default path for all other routes not defined above
@app.route('/<path:path>')
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/post-stamp', methods=['POST'])
def post_stamp():
    data = request.get_json()
    print(data)
    cs.run_stamp(data)
    return 'Success!', 200


if __name__ == "__main__":
    app.run(port=8000, debug=False)
