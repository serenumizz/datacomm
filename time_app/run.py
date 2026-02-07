from flask import Flask
from datetime import datetime, timezone
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/time')
def get_time():
    return datetime.now(timezone.utc).strftime("%H:%M:%S %Z")


app.run(host='0.0.0.0',
        port=8080,
        debug=True)