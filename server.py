from flask import Flask, jsonify
from flask_cors import CORS
import speedtest
import logging
import threading

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Global variable to store the download speed result
download_result = {"download": None}

def measure_download_speed():
    """Measures internet download speed asynchronously."""
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        download_speed = test.download(threads=None) / 1_000_000  # Convert to Mbps
        download_result["download"] = round(download_speed, 2)
        logging.info(f"Download speed: {download_result['download']} Mbps")
    except Exception as e:
        logging.error(f"Download speed measurement failed: {e}")
        download_result["download"] = "Error"

@app.route("/", methods=["GET"])
def get_download_speed():
    if download_result["download"] is None:
        # Start the download speed test in a background thread
        threading.Thread(target=measure_download_speed).start()
        return jsonify({'status': 'Download speed test started, please check back later.'})
    elif download_result["download"] == "Error":
        return jsonify({'error': 'Download speed measurement failed'}), 500
    else:
        # Prepare the result and reset the global variable for the next request
        response = {'download': download_result["download"]}
        download_result["download"] = None
        return jsonify(response)
