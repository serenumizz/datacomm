import os
import socket
import threading
import time
import services as serv
from flask import Flask, request, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

# UDP_HOST = os.getenv("UDP_HOST", "host.docker.internal")
UDP_HOST = os.getenv("UDP_HOST", "authoritative-server")
UDP_PORT = int(os.getenv("UDP_PORT", 9090))


# ==============================
# HTTP Endpoint
# ==============================
TTL = 86400

@app.route("/")
def home():
    return "alive"

# @app.before_first_request
def startup():
    while True:
        serv.register_with_authoritative(UDP_HOST, UDP_PORT)
        time.sleep(TTL - 2)

@app.route('/register', methods=["PUT"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = data.get("as_port")

    if not all([hostname, ip, as_ip, as_port]):
        return jsonify({"error": "Missing fields"}), 400

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # connect to dummy address
        s.connect(("8.8.8.8", 80))
        # ip = s.getsockname()[0]
    finally:
        s.close()
    message = f"""TYPE=A
        NAME={hostname} VALUE={ip} TTL=86400
        """
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.sendto(message.encode(), (UDP_HOST, UDP_PORT))
    sock.sendto(message.encode(), (as_ip, int(as_port)))

    response, _ = sock.recvfrom(1024)

    return jsonify({
        "authoritative_response": response.decode()
    }), 201

@app.route("/fibonacci", methods=['GET'])
def compute_fibonacci():
    number = request.args.get("number")

    if not number:
        return jsonify({"error": "number is required"}), 400
    msg, err_code = serv.handle_value_type(number)
    if err_code != 200:
        return jsonify({
        "result": msg,
        "status": err_code
    })

    n = int(number)
    result = serv.fibonacci(n)
    return jsonify({
        "result": result,
        "status": 200
    })
    
if __name__ == "__main__":
    threading.Thread(target=startup, daemon=True).start()
    app.run(host='0.0.0.0',
            port=9090)