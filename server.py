from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# # Configure logging to print errors
# logging.basicConfig(level=logging.DEBUG)

def measure_download_speed():
    """Measures internet download speed."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()  # Select the best server based on latency
        download_speed = test.download() / 1_000_000  # Convert to Mbps
        return download_speed
    except Exception as e:
        logging.error(f"Download speed measurement failed: {e}")
        raise



@app.route('/', methods=['GET'])
def download_speed():
    try:
        download_speed_mbps = measure_download_speed()
        return jsonify({'download': download_speed_mbps})
    except Exception as e:
        logging.error("Download speed measurement failed:", exc_info=e)
        return jsonify({'error': 'Download speed measurement failed'}), 500

