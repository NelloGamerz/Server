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
