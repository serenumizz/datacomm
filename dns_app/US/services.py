import time
import logging
import requests
import socket
from flask import request, jsonify

# ==============================
# Function
# ==============================

def handle_request():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port", type=int)
    number = request.args.get("number", type=int)
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port", type=int)
    msg = 'success'
    err_code = 200

    # =========================
    # Validation
    # =========================

    if not hostname:
        return {"msg": "Missing hostname"}, 400

    if fs_port is None:
        return {"msg": "Invalid or missing fs_port"}, 400

    if number is None:
        return {"msg": "Invalid or missing number"}, 400

    if not as_ip:
        return {"msg": "Missing as_ip"}, 400

    if as_port is None:
        return {"msg": "Invalid or missing as_port"}, 400
    
    return {'msg': msg}, err_code


def parse_dns_response(message):
    lines = message.strip().split("\n")

    if len(lines) < 2:
        return None, "Invalid DNS response format"

    # Check TYPE
    if lines[0].strip() != "TYPE=A":
        return None, "Unsupported TYPE"

    fields = {}

    parts = lines[1].split()
    for part in parts:
        if "=" not in part:
            return None, "Invalid field format"
        key, value = part.split("=")
        fields[key] = value

    # Validate required fields
    required_fields = ["NAME", "VALUE", "TTL"]
    for field in required_fields:
        if field not in fields:
            return None, f"Missing {field}"

    return fields, None


# /fibonacci?hostname=fibonacci.com&fs_port=K&number=X&as_ip=Y
# &as_port= Z
def ip_request(hostname, as_ip, as_port):
    message = f"TYPE=A\nNAME={hostname}"


    logging.basicConfig(level=logging.INFO)
    logging.info(f"debug {message}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (as_ip, int(as_port)))

    response, _ = sock.recvfrom(1024)

    # return response.decode(), 200
    fields, error = parse_dns_response(response.decode())

    if error:
        return f"DNS Error {message}", 400
    else:
        ip_address = fields["VALUE"]
        ttl = int(fields["TTL"])

        return ip_address, 200
    
def fibonacci_server(ip, port, number):
    try:
        # Use an external service that returns only the IP address
        print(f"http://{ip}:{port}/fibonacci?number={number}")
        response = requests.get(f"http://{ip}:{port}/fibonacci?number={number}")
        return response.json(), response.status_code

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500