from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.DEBUG)

# Global dictionary to store the upload speed and ping results
speedtest_results = {"upload": None, "ping": None}

def measure_upload_ping():
    """Measures internet upload speed and ping asynchronously."""
    try:
        test = speedtest.Speedtest(timeout=5)
        test.get_best_server()  # Select the best server based on latency
        upload_speed = test.upload() / 1_000_000  # Convert to Mbps
        ping = test.results.ping  # Ping in milliseconds

        # Store the results
        speedtest_results["upload"] = round(upload_speed, 2)
        speedtest_results["ping"] = round(ping, 2)

        logging.info(f"Upload speed: {speedtest_results['upload']} Mbps, Ping: {speedtest_results['ping']} ms")
    except Exception as e:
        logging.error(f"Upload/Ping measurement failed: {e}")
        speedtest_results["upload"] = "Error"
        speedtest_results["ping"] = "Error"

@app.route("/", methods=["GET"])
def upload_ping():
    if speedtest_results["upload"] is None or speedtest_results["ping"] is None:
        # Start the speed test in a background thread
        threading.Thread(target=measure_upload_ping).start()
        return jsonify({"status": "Speed test started, please check back later."})
    elif speedtest_results["upload"] == "Error" or speedtest_results["ping"] == "Error":
        return jsonify({"error": "Failed to measure upload speed and ping"}), 500
    else:
        return jsonify({"upload": speedtest_results["upload"], "ping": speedtest_results["ping"]})
