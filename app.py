from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('public', '/')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    app.run()
