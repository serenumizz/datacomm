import socket
import json
import os
import time

HOST = "0.0.0.0"
PORT = 53533
DB_FILE = "dns_records.json"


# ==============================
# Database Handling
# ==============================

def load_db():
    if not os.path.exists(DB_FILE):
        return {}

    if os.path.getsize(DB_FILE) == 0:
        return {}

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


dns_db = load_db()


# ==============================
# Message Parsing
# ==============================

def parse_message(message):
    lines = message.strip().split("\n")

    if len(lines) < 2:
        return None, "Invalid format"

    # Check TYPE
    if lines[0].strip() != "TYPE=A":
        return None, "Only TYPE=A supported"

    fields = {}

    parts = lines[1].split()
    for part in parts:
        if "=" not in part:
            return None, "Invalid field format"
        key, value = part.split("=")
        fields[key] = value

    return fields, None


def get_request_type(fields):
    if "VALUE" in fields and "TTL" in fields:
        return "REGISTER"
    elif "NAME" in fields and "VALUE" not in fields:
        return "QUERY"
    else:
        return "INVALID"


# ==============================
# Registration Handler
# ==============================

def handle_registration(fields, addr, sock):
    name = fields["NAME"]
    value = fields["VALUE"]
    ttl = int(fields["TTL"])

    dns_db[name] = {
        "TYPE": "A",
        "VALUE": value,
        "TTL": ttl,
        "TIMESTAMP": time.time()
    }

    save_db(dns_db)

    print(f"[REGISTER] {name} -> {value} (TTL={ttl})")
    sock.sendto(b"201", addr)


# ==============================
# Query Handler
# ==============================

def handle_query(fields, addr, sock):
    name = fields["NAME"]
    print("DEBUG NAME", name)

    if name not in dns_db:
        print("CHECK DNS DB", dns_db)
        sock.sendto(b"NAME NOT IN MESSAGE", addr)
        return

    record = dns_db[name]

    # TTL expiration check
    current_time = time.time()
    elapsed = current_time - record["TIMESTAMP"]

    if elapsed > record["TTL"]:
        print(f"[EXPIRED] {name}")
        del dns_db[name]
        save_db(dns_db)
        sock.sendto(b"NOT FOUND", addr)
        return

    response = f"""TYPE=A
        NAME={name} VALUE={record['VALUE']} TTL={record['TTL']}
        """

    print(f"[QUERY] {name} -> {record['VALUE']}")
    sock.sendto(response.encode(), addr)


# ==============================
# UDP Server Start
# ==============================

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    print(f"Authoritative Server running on UDP port {PORT}...")

    while True:
        message, addr = sock.recvfrom(1024)
        message = message.decode()

        print(f"\nReceived from {addr}:")
        print(message)

        fields, error = parse_message(message)

        if error:
            sock.sendto(f"ERROR: {error}".encode(), addr)
            continue

        request_type = get_request_type(fields)

        if request_type == "REGISTER":
            handle_registration(fields, addr, sock)

        elif request_type == "QUERY":
            handle_query(fields, addr, sock)

        else:
            sock.sendto(b"INVALID REQUEST", addr)


if __name__ == "__main__":
    start_server()