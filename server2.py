from flask import Flask, jsonify, request
from flask_cors import CORS
import speedtest
import logging
import threading

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Global dictionary to store the test results
speedtest_results = {"upload": None, "ping": None, "server": None}

def measure_upload_ping():
    """Measures upload speed and ping using the nearest server."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()  # Automatically selects the best server based on latency

        # Get server details
        server = test.results.server["host"]

        # Measure upload speed
        upload_speed = test.upload(threads=1) / 1_000_000  # Convert to Mbps
        ping = test.results.ping  # Get ping in milliseconds

        # Store the results
        speedtest_results["upload"] = round(upload_speed, 2)
        speedtest_results["ping"] = round(ping, 2)
        speedtest_results["server"] = server

        logging.info(f"Upload speed: {speedtest_results['upload']} Mbps, Ping: {speedtest_results['ping']} ms, Server: {server}")
    except Exception as e:
        logging.error(f"Measurement failed: {e}")
        speedtest_results["upload"] = "Error"
        speedtest_results["ping"] = "Error"
        speedtest_results["server"] = "N/A"

@app.route("/", methods=["GET"])
def upload_ping():
    user_ip = request.remote_addr
    logging.info(f"User IP: {user_ip}")

    if speedtest_results["upload"] is None or speedtest_results["ping"] is None:
        threading.Thread(target=measure_upload_ping).start()
        return jsonify({"status": "Speed test in progress, please check back later."})
    elif speedtest_results["upload"] == "Error":
        return jsonify({"error": "Measurement failed"}), 500
    else:
        return jsonify({
            "upload": speedtest_results["upload"],
            "ping": speedtest_results["ping"],
            "server": speedtest_results["server"]
        })
