import socket

def register_with_authoritative(UDP_HOST, UDP_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # connect to dummy address
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    message = f"""TYPE=A
        NAME=fibonacci.com VALUE={ip} TTL=86400
        """
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (UDP_HOST, UDP_PORT))

    # response, _ = sock.recvfrom(1024)

    sock.close()

    print("Registered with Authoritative Server")

    # return response.decode()

def handle_value_type(n):
    try:
        n = int(n)
        return "Value in integer", 200
    except (ValueError, TypeError):
        return "Value should be an integer", 400

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)