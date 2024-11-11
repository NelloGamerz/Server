from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging
import threading

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Global variable to store upload speed and ping results
upload_ping_result = {"upload": None, "ping": None}

def measure_upload_ping():
    """Measures internet upload speed and ping asynchronously."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        upload_speed = test.upload(threads=None) / 1_000_000  # Convert to Mbps
        ping = test.results.ping  # Ping in milliseconds
        upload_ping_result["upload"] = round(upload_speed, 2)
        upload_ping_result["ping"] = round(ping, 2)
        logging.info(f"Upload speed: {upload_ping_result['upload']} Mbps, Ping: {upload_ping_result['ping']} ms")
    except Exception as e:
        logging.error(f"Upload/Ping measurement failed: {e}")
        upload_ping_result.update({"upload": "Error", "ping": "Error"})

@app.route("/", methods=["GET"])
def get_upload_ping():
    if upload_ping_result["upload"] is None:
        # Start the upload speed and ping test in a background thread
        threading.Thread(target=measure_upload_ping).start()
        return jsonify({'status': 'Upload and ping speed test started, please check back later.'})
    elif upload_ping_result["upload"] == "Error":
        return jsonify({'error': 'Upload speed and ping measurement failed'}), 500
    else:
        # Prepare the result and reset the global variable for the next request
        response = {'upload': upload_ping_result["upload"], 'ping': upload_ping_result["ping"]}
        upload_ping_result.update({"upload": None, "ping": None})
        return jsonify(response)
