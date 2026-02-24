import socket
import argparse

def test_regis():
    message = """TYPE=A
    NAME=fibonacci.com VALUE=3.4.5.6 TTL=10
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), ("127.0.0.1", 53533))

    response, _ = sock.recvfrom(1024)
    print(response.decode())

def test_request():
    message = """TYPE=A
    NAME=fibonacci.com
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), ("127.0.0.1", 53533))

    response, _ = sock.recvfrom(1024)
    print(response.decode())


parser = argparse.ArgumentParser(description ='request or regist')
parser.add_argument(
    '--func',
    type=str,
    default='regist',
    help='The function'
)
args = parser.parse_args()


if args.func == "regis":
    print(args)
    test_regis()
if args.func == "request":
    print(args)
    test_request()



