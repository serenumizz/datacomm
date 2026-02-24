from flask import Flask, request, jsonify
import time
import services as serv

app = Flask(__name__)

# ==============================
# Main
# ==============================


# 1. hit AS
# 2. Get FS ip address
# 3. hit FS
# 4. get result

@app.route("/fibonacci", methods=['GET'])
def compute_fibonacci():
    response, err_code = serv.handle_request()
    if err_code != 200:
        return jsonify(response), err_code

    hostname = request.args.get("hostname")
    number = request.args.get("number", 0)
    as_ip = request.args.get("as_ip").strip()
    as_port = request.args.get("as_port")
    fs_port = request.args.get("fs_port")

    # 1. hit AS
    try:
        msg, err_code = serv.handle_request()
        # return msg

    # 2. Get FS ip address
        ip_address, err_code = serv.ip_request(hostname, as_ip, as_port)

    # 3. hit FS
        try:
            response, err_code = serv.fibonacci_server(ip_address, fs_port, number)
            # 4. get result
            if err_code == 200:
                return jsonify(response), 200
            else:
                return jsonify({"msg": response}), 400
        except Exception as e:
            return jsonify({"error" : str(e)}), 400
    except Exception as e:
        return jsonify({"error" : str(e)}), 400
        

if __name__ == "__main__":
    time.sleep(3)  # wait AS to be ready
    # register_to_as()
    app.run(host="0.0.0.0", port=8000)
