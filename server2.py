from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def measure_upload_ping():
    """Measures internet upload speed and ping."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()  # Select the best server based on latency
        upload_speed = test.upload() / 1_000_000  # Convert to Mbps
        ping = test.results.ping  # Ping in milliseconds
        return upload_speed, ping
    except Exception as e:
        logging.error(f"Upload/Ping measurement failed: {e}")
        raise

@app.route("/", methods=["GET"])
def upload_ping():
    try:
        upload_speed, ping = measure_upload_ping()
        return jsonify({"upload": upload_speed, "ping": ping})
    except Exception as e:
        logging.error(f"Error in /api/speedtest/upload_ping: {e}")
        return jsonify({"error": "Failed to measure upload speed and ping"}), 500
